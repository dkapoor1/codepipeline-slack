import slack
import os
import boto3
from flask import Flask, request, Response
from pathlib import Path
from dotenv import load_dotenv

# Import SLACK_TOKEN and SIGNING_SECRET for integration with local Slack instance.
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize Flask, used to send /slash commands.
app = Flask(__name__)

# Initialize SDK's for Slack (slack.WebClient) and AWS (boto3) integration.
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
codepipeline = boto3.client('codepipeline')

# Returns names of all CodePipeline pipelines.
@app.route('/pipelines', methods=['POST'])
def pipelines():
    data = request.form
    channel_id = data.get('channel_id')
    response = codepipeline.list_pipelines(
        maxResults=10
    )
    for pipeline in response['pipelines']:
        pipelineInfo = ""
        pipelineInfo += "Name: " + pipeline['name'] + "\n"
        pipelineInfo += "Created: " + pipeline['created'].strftime("%m/%d/%Y, %H:%M:%S") + "\n"
        pipelineInfo += "Updated: " + pipeline['updated'].strftime("%m/%d/%Y, %H:%M:%S") + "\n"
        client.chat_postMessage(channel=channel_id, text=pipelineInfo)
    return Response(), 200

# Lists detailed information about the requested pipeline. Pass in pipeline name as an argument.
@app.route('/pipeline_detail', methods=['POST'])
def pipeline_detail():
    data = request.form
    channel_id = data.get('channel_id')
    pipelineName = data.get('text', None)
    try:
        response = codepipeline.get_pipeline(
            name=pipelineName
        )
    except Exception as e:
        return(str(e))
    pipelineInfo = "Name: " + response['pipeline']['name'] + "\n"
    pipelineInfo += "Version: " + str(response['pipeline']['version']) + "\n"
    pipelineInfo += "Created: " + response['metadata']['created'].strftime("%m/%d/%Y, %H:%M:%S") + "\n"
    pipelineInfo += "Updated: " + response['metadata']['updated'].strftime("%m/%d/%Y, %H:%M:%S") + "\n"
    pipelineInfo += "Artifact Location: " + response['pipeline']['artifactStore']['location'] + "\n"
    pipelineInfo += "Artifact Type: " + response['pipeline']['artifactStore']['type'] + "\n"
    for stage in response['pipeline']['stages']:
        pipelineInfo += "Stage Name: " + stage['name'] + "\n"
        for action in stage['actions']:
            pipelineInfo += "    Action Name: " + action['name'] + "\n"
            pipelineInfo += "        Action Region: " + action['region'] + "\n"
            pipelineInfo += "        Action Order: " + str(action['runOrder']) + "\n"
    client.chat_postMessage(channel=channel_id, text=pipelineInfo)
    return Response(), 200

# Lists information about 5 most recent pipeline executions. Pass in pipeline name as an argument.
@app.route('/pipeline_executions', methods=['POST'])
def pipeline_executions():
    data = request.form
    channel_id = data.get('channel_id')
    pipelineName = data.get('text', None)
    try:
        response = codepipeline.list_pipeline_executions(
            pipelineName=pipelineName,
            maxResults=5
        )
    except Exception as e:
        return(str(e))
    pipelineInfo = ""
    for execution in response['pipelineExecutionSummaries']:
        pipelineInfo += "Execution ID: " + execution['pipelineExecutionId'] + "\n"
        pipelineInfo += "    Status: " + execution['status'] + "\n"
        pipelineInfo += "    Start Time: " + execution['startTime'].strftime("%m/%d/%Y, %H:%M:%S") + "\n"
        pipelineInfo += "    Last Update: " + execution['lastUpdateTime'].strftime("%m/%d/%Y, %H:%M:%S") + "\n"
        pipelineInfo += "    Trigger: " + execution['trigger']['triggerType'] + "\n"
    client.chat_postMessage(channel=channel_id, text=pipelineInfo)
    return Response(), 200

# Returns the status of the most recent run for all pipelines.
@app.route('/pipelines_status_all', methods=['POST'])
def pipelines_status_all():
    data = request.form
    channel_id = data.get('channel_id')
    response = codepipeline.list_pipelines(
        maxResults=10
    )
    for pipeline in response['pipelines']:
        pipelineInfo = ""
        pipelineInfo += "Name: " + pipeline['name'] + "\n"
        pipelineStatus = codepipeline.list_pipeline_executions(
            pipelineName=pipeline['name'],
            maxResults=1
        )
        pipelineInfo += "    Status: " + pipelineStatus['pipelineExecutionSummaries'][0]['status'] + "\n"
        pipelineInfo += "    Start Time: " + pipelineStatus['pipelineExecutionSummaries'][0]['startTime'].strftime("%m/%d/%Y, %H:%M:%S") + "\n"
        client.chat_postMessage(channel=channel_id, text=pipelineInfo)
    return Response(), 200

# Triggers pipeline start. Pass in pipeline name as an argument.
@app.route('/pipeline_start', methods=['POST'])
def pipeline_start():
    data = request.form
    channel_id = data.get('channel_id')
    pipelineName = data.get('text', None)
    try:
        response = codepipeline.start_pipeline_execution(
            name=pipelineName
        )
    except Exception as e:
        return(str(e))        
    client.chat_postMessage(channel=channel_id, text=f"Starting {pipelineName}. pipelineExecutionId is {response['pipelineExecutionId']}")
    return Response(), 200

if __name__ == "__main__":
    app.run(debug=True)