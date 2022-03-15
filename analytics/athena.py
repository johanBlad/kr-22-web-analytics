import boto3
import pythena

# Connect to a database and override default profile in your aws configuration
athena_client = pythena.Athena(database="kr22_web_event_database", session=boto3.session.Session(profile_name="netlight"))

athena_client.
