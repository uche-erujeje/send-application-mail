from chalice import Chalice
import boto3
import os

app = Chalice(app_name="send-app-mail")
ses_client = boto3.client("ses", region_name="eu-west-1")  # Change region if necessary

# Change this to your verified email address in AWS SES
SENDER_EMAIL = "hr@eandeafrica.com"

@app.route('/send-email', methods=['POST'])
def send_email():
    request = app.current_request.json_body
    name = request.get("name")
    email = request.get("email")

    if not name or not email:
        return {"error": "Missing name or email"}

    message = f"""Subject: Thank You for Applying to EANDÉ Africa

Dear {name},

Thank you for your interest in joining EANDÉ Africa. We appreciate the time and effort you put into your application and look forward to learning more about you. Our goal is to make this process as smooth and straightforward as possible.

About EANDÉ Africa  
At EANDÉ, we are dedicated to redefining excellence in the luxury industry. Our mission is to set new standards by delivering exceptional experiences and services that elevate the perception of luxury in Africa and beyond. Through LUXFRICA, we empower luxury brands with innovative digital solutions, shaping the future of luxury retail.

Next Steps  
Our hiring process consists of four key steps:  
1. Application Review – You have already completed the first step by submitting your application.  
2. Assessment – We will review all applications and send assessment links to successful candidates within the next week.  
3. Interview – Once you complete the assessment, we will schedule an interview.  
4. Final Selection – After interviews, we will select the best candidates and extend offers.

We appreciate your patience as we carefully review each application. If this role is not the right fit at this time, we encourage you to stay connected for future opportunities as we continue to grow.

Thank you again for considering EANDÉ Africa. We look forward to the possibility of working together.

Best regards,  
EANDÉ Africa Team
"""

    response = ses_client.send_email(
        Source=SENDER_EMAIL,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": "Your Application to EANDÉ Africa"},
            "Body": {"Text": {"Data": message}}
        }
    )

    return {"message": "Email sent successfully", "response": response}
