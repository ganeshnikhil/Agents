import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .get_env import EnvManager
from data.email_schema import email_prompts 
from ...Brain.text_to_info import send_to_ai

class EmailSender:
    def __init__(self):
        # Load email credentials from environment variables
        self.smtp_server = "smtp.gmail.com"
        self.port = 587
        self.password = EnvManager.load_variable("Password_email")
        self.receiver_email = EnvManager.load_variable("Reciever_email")
        self.sender_email = EnvManager.load_variable("Sender_email")
    
    def initate_email(self, subject: str, email_content: str) -> bool:
        """Send an email with the provided subject and content."""
        html_content = f"""
        <html>
        <body>
        <p>{email_content}</p>
        </body>
        </html>"""
        
        try:
            # Prepare the email
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.receiver_email
            msg['Subject'] = subject.strip()
            msg.attach(MIMEText(html_content, 'html'))
            
            # Set up the secure SSL context and send the email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, self.receiver_email, msg.as_string())
                print("Email sent successfully...")
        except Exception as e:
            print(f"Error: {e}")
            return False
        return True

    def email_content(self) -> dict:
        """Generate and send an automated email based on selected template."""
        select_template = input("Select an email template (job, friend, meeting, doctor, leave, product): ")
        if select_template not in email_prompts:
            print("[+] Invalid template selection.")
            return {}
        
        # Fetch the selected template
        template = email_prompts[select_template]
        placeholders = {}
        
        # Collect placeholder values for the email template
        for placeholder in template['prompt'].split('{')[1:]:
            placeholder_key = placeholder.split('}')[0]
            value = input(f"Enter value for '{placeholder_key}': ").strip()
            if not value:
                print(f"Value for '{placeholder_key}' cannot be empty.")
                return {}
            placeholders[placeholder_key] = value
        
        # Format the prompt with placeholders
        formatted_prompt = template['prompt'].format(**placeholders)
        
        # Display the prompt for review
        print("----- Start prompt -----")
        print(formatted_prompt)
        print("----- End prompt -----")
        
        # Generate email content using AI
        email_prompt = "You are a professional email writer. Write an email based on the provided content in less than 20 words."
        complete_prompt = f"{email_prompt}\n{formatted_prompt}"
        response = send_to_ai(complete_prompt).strip()
        
        # Generate email subject using AI
        sub_prompt = f"Give a suitable subject for the given email: {response}. Use 3-4 words max."
        subject = send_to_ai(sub_prompt).strip()
        
        # Return the generated subject and content
        return {'subject': subject, 'content': response}

def send_email():
    email_sender = EmailSender()
    email_details = email_sender.email_content()
    
    if email_details:
        subject = email_details['subject']
        content = email_details['content']
        flag = email_sender.initate_email(subject, content)
        return flag 
    return False

# Example Usage:
if __name__ == "__main__":
    email_sender = EmailSender()
    
    # Generate and send the email
    email_details = email_sender.send_email()
    
    if email_details:
        subject = email_details['subject']
        content = email_details['content']
        email_sender.initate_email(subject, content)
