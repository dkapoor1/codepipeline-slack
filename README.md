# codepipeline-slack

codepipeline-slack is a Slack app that supports interacting with AWS CodePipeline using Slack.

These are the following slash commands supported:

`/pipelines` </br>
Returns all CodePipeline pipelines

`/pipelines_status_all` </br>
Returns the status of the most recent run for all pipelines

`/pipeline_detail <pipeline-name>` </br>
Lists detailed information about the requested pipeline

`/pipeline_executions <pipeline-name>` </br>
Lists information about 5 most recent pipeline executions

`/pipeline_start <pipeline-name>` </br>
Triggers start of the provided pipeline
