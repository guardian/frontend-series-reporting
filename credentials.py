import boto3
import ConfigParser
import io

session=boto3.session.Session(region_name = 'eu-west-1')
s3 = session.resource('s3')

credentialsBucket = 'aws-frontend-artifacts'
credentialsSection = 'redshift_connection_config'
credentialsKeys = 'lambda/credentials/redshift_connection_config.py'

bucket = s3.Bucket(credentialsBucket)


def fileToCredentials(fileLike):
    parser = ConfigParser.ConfigParser()
    parser.readfp(fileLike)

    return "host='{host}' port='{port}'  dbname='{dbname}' user='{user}' password='{password}'".format(
        host= parser.get(credentialsSection, 'host'),
        port= parser.get(credentialsSection, 'port'),
        dbname= parser.get(credentialsSection, 'dbname'),
        user= parser.get(credentialsSection, 'user'),
        password= parser.get(credentialsSection, 'password')
    )



def getRedshiftCredentials():
    credentialsFile = io.BytesIO(bucket.Object(credentialsKeys).get()['Body'].read())
    return fileToCredentials(credentialsFile)