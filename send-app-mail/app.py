from chalice import Chalice
import boto3
import os

app = Chalice(app_name="send-app-mail")
ses_client = boto3.client("ses", region_name="eu-west-1")  # Change region if necessary

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
#TABLE_NAME = os.environ.get("TABLE_NAME", "EmailsTable")
table = dynamodb.Table(TABLE_NAME)

# Change this to your verified email address in AWS SES
SENDER_EMAIL = "hr@eandeafrica.com"

@app.route('/send-email', methods=['POST'])
def send_email():
    request = app.current_request.json_body
    name = request.get("name")
    email = request.get("email")

    if not name or not email:
        return {"error": "Missing name or email"}

    message = f"""Dear {name},

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
            "Subject": {"Data": "Thank You for Applying to EANDÉ Africa"},
            "Body": {"Text": {"Data": message}}
        }
    )

    return {"message": "Email sent successfully", "response": response}


@app.route('/send-bulk-email', methods=['POST'])
def send_bulk_email():
    request = app.current_request.json_body
    recipients = request.get("emails", [])  # Expecting a list of emails

    if not recipients or not isinstance(recipients, list):
        return {"error": "Invalid or missing email list"}

    message = """
Dear Applicant,

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
        Destination={"ToAddresses": recipients},
        Message={
            "Subject": {"Data": "Thank You for Applying to EANDÉ Africa"},
            "Body": {"Text": {"Data": message}}
        }
    )

    return {"message": "Bulk email sent successfully", "response": response}


@app.route('/store-emails', methods=['POST'])
def store_emails():
    """Stores multiple emails under the same category in DynamoDB"""
    request = app.current_request.json_body
    category = request.get("category")
    emails = request.get("emails")

    if not category or not isinstance(emails, list) or not emails:
        return Response(body={"error": "Category and a non-empty list of emails are required."}, status_code=400)

    # Store each email separately in DynamoDB
    with table.batch_writer() as batch:
        for email in emails:
            batch.put_item(Item={"email": email, "category": category})

    return {"message": f"{len(emails)} emails stored successfully!", "category": category}

@app.route('/get-emails/{category}', methods=['GET'])
def get_emails_by_category(category):
    """Fetch emails by category"""
    response = table.scan(
        FilterExpression="category = :category",
        ExpressionAttributeValues={":category": category}
    )
    emails = [item["email"] for item in response.get("Items", [])]
    return {"category": category, "emails": emails}

@app.route('/get-emails', methods=['GET'])
def get_all_emails():
    """Fetch all stored emails from DynamoDB"""
    response = table.scan()
    emails = [{"email": item["email"], "category": item["category"]} for item in response.get("Items", [])]
    return emails


@app.route('/send-emails/{category}', methods=['POST'])
def send_emails(category):
    """Sends an email to all users in the given category with a custom message"""
    request = app.current_request.json_body
    subject = request.get("subject", "No Subject Provided")
    message_body = request.get("message", "No message content provided.")

    response = table.scan(
        FilterExpression="category = :category",
        ExpressionAttributeValues={":category": category}
    )
    emails = [item["email"] for item in response.get("Items", [])]

    if not emails:
        return Response(body={"error": "No emails found for this category."}, status_code=404)

    # Send emails via AWS SES
    for email in emails:
        try:
            ses_client.send_email(
                Source=SES_SENDER_EMAIL,
                Destination={"ToAddresses": [email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": message_body}}
                }
            )
        except Exception as e:
            return Response(body={"error": str(e)}, status_code=500)

    return {"message": f"Emails sent successfully to {len(emails)} recipients in {category} category."}
