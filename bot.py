import slack
import os
import boto3
from flask import Flask, request, Response
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
codepipeline = boto3.client('codepipeline')

@app.route('/pipelines', methods=['POST'])
def pipelines():
    data = request.form
    channel_id = data.get('channel_id')
    response = codepipeline.list_pipelines(
        maxResults=10
    )
    for pipeline in response['pipelines']:
        pipelineInfo = ""
        pipelineInfo += "Name: " + pipeline['name']
        pipelineInfo += "\n" + "Created: " + pipeline['created'].strftime("%m/%d/%Y, %H:%M:%S")
        pipelineInfo += "\n" + "Updated: " + pipeline['updated'].strftime("%m/%d/%Y, %H:%M:%S")
        client.chat_postMessage(channel=channel_id, text=pipelineInfo)
    return Response(), 200

@app.route('/pipeline_detail', methods=['POST'])
def pipeline_detail():
    data = request.form
    channel_id = data.get('channel_id')
    pipelineName = request.form.get('text', None)
    response = codepipeline.get_pipeline(
        name=pipelineName
    )
    pipelineInfo = "Name: " + response['pipeline']['name']
    pipelineInfo += "\n" + "Version: " + str(response['pipeline']['version'])
    pipelineInfo += "\n" + "Created: " + response['metadata']['created'].strftime("%m/%d/%Y, %H:%M:%S")
    pipelineInfo += "\n" + "Updated: " + response['metadata']['updated'].strftime("%m/%d/%Y, %H:%M:%S")
    pipelineInfo += "\n" + "Artifact Location: " + response['pipeline']['artifactStore']['location']
    pipelineInfo += "\n" + "Artifact Type: " + response['pipeline']['artifactStore']['type']
    for stage in response['pipeline']['stages']:
        pipelineInfo += "\n" + "Stage Name: " + stage['name']
        for action in stage['actions']:
            pipelineInfo += "\n" + "    Action Name: " + action['name']
            pipelineInfo += "\n" + "        Action Region: " + action['region']
            pipelineInfo += "\n" + "        Action Order: " + str(action['runOrder'])
    client.chat_postMessage(channel=channel_id, text=pipelineInfo)
    return Response(), 200

@app.route('/pipeline_executions', methods=['POST'])
def pipeline_executions():
    data = request.form
    channel_id = data.get('channel_id')
    pipelineName = request.form.get('text', None)
    response = codepipeline.list_pipeline_executions(
        pipelineName=pipelineName,
        maxResults=5
    )
    pipelineInfo = ""
    for execution in response['pipelineExecutionSummaries']:
        pipelineInfo += "Execution ID: " + execution['pipelineExecutionId'] + "\n"
        pipelineInfo += "    Status: " + execution['status'] + "\n"
        pipelineInfo += "    Start Time: " + execution['startTime'].strftime("%m/%d/%Y, %H:%M:%S") + "\n"
        pipelineInfo += "    Last Update: " + execution['lastUpdateTime'].strftime("%m/%d/%Y, %H:%M:%S") + "\n"
        pipelineInfo += "    Trigger: " + execution['trigger']['triggerType'] + "\n"
    client.chat_postMessage(channel=channel_id, text=pipelineInfo)
    return Response(), 200

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

@app.route('/pipeline_start', methods=['POST'])
def pipeline_start():
    data = request.form
    channel_id = data.get('channel_id')
    pipelineName = request.form.get('text', None)
    response = codepipeline.start_pipeline_execution(
        name=pipelineName
    )
    client.chat_postMessage(channel=channel_id, text=f"Starting {pipelineName}. pipelineExecutionId is {response['pipelineExecutionId']}")
    return Response(), 200

if __name__ == "__main__":
    app.run(debug=True)