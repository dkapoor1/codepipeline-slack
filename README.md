# codepipeline-slack

codepipeline-slack is a Slack app that supports interacting with AWS CodePipeline using Slack.

These are the following slash commands supported:

/pipelines
Returns all CodePipeline pipelines

/pipelines_status_all
Returns the status of the most recent run for all pipelines

/pipeline_detail <pipeline-name>
Lists detailed information about the requested pipeline

/pipeline_executions <pipeline-name>
Lists information about 5 most recent pipeline executions

/pipeline_start <pipeline-name>
Triggers start of the provided pipeline
