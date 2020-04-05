import requests
import os
import sys


def provisioner(microservice_name, namespace_name, microservice_framework):
    bitbucket_api_url = "https://api.bitbucket.org/2.0"
    bitbucket_username = ""                                                 # BITBUCKET REPOSITORY OWNER NAME
    bitbucket_auth_user = ""                                                # BITBUCKET USERNAME
    bitbucket_auth_password = os.environ["BITBUCKET_AUTH_PASSWORD"]         # BITBUCKET PASSWORD
    bitbucket_header = {'Content-Type': 'application/json'}
    jenkins_api_url = ""                                                    # JENKINS SERVER URL
    jenkins_auth_user = ""                                                  # JENKINS USERNAME
    jenkins_auth_password = os.environ["JENKINS_AUTH_PASSWORD"]             # JENKINS PASSWORD
    jenkins_header = {'Content-Type': 'text/xml'}
    slack_token = os.environ["SLACK_TOKEN"]                                 # SLACK TOKEN
    slack_header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + slack_token}
    dba_slack_channel = "#dba-notifications"

    # Bitbucket Variables
    repository_url = bitbucket_api_url + "/repositories/" + bitbucket_username + "/" + microservice_name
    commit_url = repository_url + "/src"
    branch_url = repository_url + "/refs/branches"
    branch_restriction_url = repository_url + "/branch-restrictions"
    access_key_url = repository_url + "/deploy-keys"
    access_key = os.environ['JENKINS_ACCESS_KEY']
    hook_url = repository_url + "/hooks"

    # Jenkins Variables
    if microservice_framework == "spring":
        hook_job_path = "microservices-hooks"
        job_path = "microservices-pipelines"
        slack_channel = "jenkins-notifications"
        pipeline_repository = "pipeline"
        repository_project = "COR"
    elif microservice_framework == "node":
        hook_job_path = "integration-api-hooks"
        job_path = "integration-api-pipelines"
        slack_channel = "integration-api-notifications"
        pipeline_repository = "integration-api-pipeline"
        repository_project = "INT"
    else:
        sys.exit("You didn't insert the available language options .")

    create_hook_job_url = jenkins_api_url + "/job/" + hook_job_path + "/createItem?name=" + microservice_name
    create_develop_job_url = jenkins_api_url + "/job/" + job_path + "/createItem?name=" + microservice_name + "-develop"
    create_staging_job_url = jenkins_api_url + "/job/" + job_path + "/createItem?name=" + microservice_name + "-staging"
    create_master_job_url = jenkins_api_url + "/job/" + job_path + "/createItem?name=" + microservice_name + "-master"
    create_hook_job_payload = """<?xml version='1.1' encoding='UTF-8'?><flow-definition plugin="workflow-job@2.31"><actions/><description></description><keepDependencies>false</keepDependencies><properties><org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty><triggers><com.cloudbees.jenkins.plugins.BitBucketTrigger plugin="bitbucket@1.1.9"><spec></spec></com.cloudbees.jenkins.plugins.BitBucketTrigger></triggers></org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty></properties><definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.63"><scm class="hudson.plugins.git.GitSCM" plugin="git@3.9.3"><configVersion>2</configVersion><userRemoteConfigs><hudson.plugins.git.UserRemoteConfig><url>git@bitbucket.org:investree/""" + microservice_name + """</url><credentialsId>private-key-for-bitbucket</credentialsId></hudson.plugins.git.UserRemoteConfig></userRemoteConfigs><branches><hudson.plugins.git.BranchSpec><name>*/master</name></hudson.plugins.git.BranchSpec><hudson.plugins.git.BranchSpec><name>*/staging</name></hudson.plugins.git.BranchSpec><hudson.plugins.git.BranchSpec><name>*/develop</name></hudson.plugins.git.BranchSpec></branches><doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations><submoduleCfg class="list"/><extensions/></scm><scriptPath>Jenkinsfile</scriptPath><lightweight>false</lightweight></definition><triggers/><disabled>false</disabled></flow-definition>"""
    create_develop_job_payload = """<?xml version='1.1' encoding='UTF-8'?><flow-definition plugin="workflow-job@2.31"><actions/><description></description><keepDependencies>false</keepDependencies><properties><com.sonyericsson.rebuild.RebuildSettings plugin="rebuild@1.31"><autoRebuild>false</autoRebuild><rebuildDisabled>false</rebuildDisabled></com.sonyericsson.rebuild.RebuildSettings><hudson.model.ParametersDefinitionProperty><parameterDefinitions><hudson.model.StringParameterDefinition><name>MS_NAME</name><description></description><defaultValue>""" + microservice_name + """</defaultValue><trim>false</trim></hudson.model.StringParameterDefinition><hudson.model.StringParameterDefinition><name>SLACK_CHANNEL</name><description></description><defaultValue>""" + slack_channel + """</defaultValue><trim>false</trim></hudson.model.StringParameterDefinition><hudson.model.StringParameterDefinition><name>MS_NAMESPACE</name><description/><defaultValue>""" + namespace_name + """</defaultValue><trim>false</trim></hudson.model.StringParameterDefinition></parameterDefinitions></hudson.model.ParametersDefinitionProperty></properties><definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.63"><scm class="hudson.plugins.git.GitSCM" plugin="git@3.9.3"><configVersion>2</configVersion><userRemoteConfigs><hudson.plugins.git.UserRemoteConfig><url>git@bitbucket.org:""" + bitbucket_username + """/""" + pipeline_repository + """</url><credentialsId>private-key-for-bitbucket</credentialsId></hudson.plugins.git.UserRemoteConfig></userRemoteConfigs><branches><hudson.plugins.git.BranchSpec><name>*/master</name></hudson.plugins.git.BranchSpec></branches><doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations><submoduleCfg class="list"/><extensions/></scm><scriptPath>""" + microservice_name + """/develop.jenkinsfile</scriptPath><lightweight>false</lightweight></definition><triggers/><disabled>false</disabled></flow-definition>"""
    create_staging_job_payload = """<?xml version='1.1' encoding='UTF-8'?><flow-definition plugin="workflow-job@2.31"><actions/><description></description><keepDependencies>false</keepDependencies><properties><com.sonyericsson.rebuild.RebuildSettings plugin="rebuild@1.31"><autoRebuild>false</autoRebuild><rebuildDisabled>false</rebuildDisabled></com.sonyericsson.rebuild.RebuildSettings><hudson.model.ParametersDefinitionProperty><parameterDefinitions><hudson.model.StringParameterDefinition><name>MS_NAME</name><description></description><defaultValue>""" + microservice_name + """</defaultValue><trim>false</trim></hudson.model.StringParameterDefinition><hudson.model.StringParameterDefinition><name>SLACK_CHANNEL</name><description></description><defaultValue>""" + slack_channel + """</defaultValue><trim>false</trim></hudson.model.StringParameterDefinition><hudson.model.StringParameterDefinition><name>MS_NAMESPACE</name><description/><defaultValue>""" + namespace_name + """</defaultValue><trim>false</trim></hudson.model.StringParameterDefinition></parameterDefinitions></hudson.model.ParametersDefinitionProperty></properties><definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.63"><scm class="hudson.plugins.git.GitSCM" plugin="git@3.9.3"><configVersion>2</configVersion><userRemoteConfigs><hudson.plugins.git.UserRemoteConfig><url>git@bitbucket.org:""" + bitbucket_username + """/""" + pipeline_repository + """</url><credentialsId>private-key-for-bitbucket</credentialsId></hudson.plugins.git.UserRemoteConfig></userRemoteConfigs><branches><hudson.plugins.git.BranchSpec><name>*/master</name></hudson.plugins.git.BranchSpec></branches><doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations><submoduleCfg class="list"/><extensions/></scm><scriptPath>""" + microservice_name + """/staging.jenkinsfile</scriptPath><lightweight>false</lightweight></definition><triggers/><disabled>false</disabled></flow-definition>"""
    create_master_job_payload = """<?xml version='1.1' encoding='UTF-8'?><flow-definition plugin="workflow-job@2.31"><actions/><description></description><keepDependencies>false</keepDependencies><properties><com.sonyericsson.rebuild.RebuildSettings plugin="rebuild@1.31"><autoRebuild>false</autoRebuild><rebuildDisabled>false</rebuildDisabled></com.sonyericsson.rebuild.RebuildSettings><hudson.model.ParametersDefinitionProperty><parameterDefinitions><hudson.model.StringParameterDefinition><name>MS_NAME</name><description></description><defaultValue>""" + microservice_name + """</defaultValue><trim>false</trim></hudson.model.StringParameterDefinition><hudson.model.StringParameterDefinition><name>SLACK_CHANNEL</name><description></description><defaultValue>""" + slack_channel + """</defaultValue><trim>false</trim></hudson.model.StringParameterDefinition><hudson.model.StringParameterDefinition><name>MS_NAMESPACE</name><description/><defaultValue>""" + namespace_name + """</defaultValue><trim>false</trim></hudson.model.StringParameterDefinition></parameterDefinitions></hudson.model.ParametersDefinitionProperty></properties><definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.63"><scm class="hudson.plugins.git.GitSCM" plugin="git@3.9.3"><configVersion>2</configVersion><userRemoteConfigs><hudson.plugins.git.UserRemoteConfig><url>git@bitbucket.org:""" + bitbucket_username + """/""" + pipeline_repository + """</url><credentialsId>private-key-for-bitbucket</credentialsId></hudson.plugins.git.UserRemoteConfig></userRemoteConfigs><branches><hudson.plugins.git.BranchSpec><name>*/master</name></hudson.plugins.git.BranchSpec></branches><doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations><submoduleCfg class="list"/><extensions/></scm><scriptPath>""" + microservice_name + """/master.jenkinsfile</scriptPath><lightweight>false</lightweight></definition><triggers/><disabled>false</disabled></flow-definition>"""
    build_url = jenkins_api_url + "/job/" + hook_job_path + "/job/" + microservice_name + "/build"

    # Slack Variables
    send_message_url = "https://slack.com/api/chat.postMessage"

    # BITBUCKET PROVISION
    create_repository = requests.post(repository_url, headers=bitbucket_header, data='{"is_private":"true","project":{"key":"' + repository_project + '"}}',
                                      auth=(bitbucket_auth_user, bitbucket_auth_password))
    print("repository creation status code : ", create_repository.status_code)
    initial_commit = requests.post(commit_url, headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                   data='.gitignore=Jenkinsfile&message=%5BTREEBOT%5D&author=DevOps%20Engineering%20Team%20%3Csysops%40investree.id%3E',
                                   auth=(bitbucket_auth_user, bitbucket_auth_password))
    print("initial commit status code: ", initial_commit.status_code)
    branches = ["develop", "staging"]
    for branch in branches:
        create_branches = requests.post(branch_url, headers=bitbucket_header, data='{"name":"' + branch + '","target":{"hash":"master"}}',
                                        auth=(bitbucket_auth_user, bitbucket_auth_password))
        print(branch, "branch creation status code : ", create_branches.status_code)
    branches.append("master")
    restriction_rules = ["delete", "force", "push"]
    for branch in branches:
        push_jenkinsfile_hook = requests.post(commit_url, auth=(bitbucket_auth_user, bitbucket_auth_password),
                                              headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                              data="author=DevOps%20Engineering%20Team%20%3Csysops%40investree.id%3E&branch=" + branch + "&message=%5BTREEBOT%5D&Jenkinsfile=build%20job%3A%20%22" + job_path + "%2F" + microservice_name + "-" + branch + "%22%2C%20wait%3A%20false")
        print("jenkinsfile hook insertion on branch", branch, "status code: ", push_jenkinsfile_hook.status_code)
        for rule in restriction_rules:
            restrict_branches = requests.post(branch_restriction_url, headers=bitbucket_header, auth=(bitbucket_auth_user, bitbucket_auth_password),
                                              data='{"kind":"' + rule + '","pattern":"' + branch + '","groups":[],"users":[]}')
            print(rule, "rule creation on ", branch, " branch status code: ", restrict_branches.status_code)
        restrict_merges = requests.post(branch_restriction_url, headers=bitbucket_header, auth=(bitbucket_auth_user, bitbucket_auth_password),
                                        data='{"kind":"restrict_merges","pattern":"' + branch + '","groups":[{"owner":{"username":"' + bitbucket_username + '"},"slug":"devops-engineers"},{"owner":{"username":"investree"},"slug":"coretree-backend-developers"}],"users":[]}')
        print("restrict merges rule creation on branch", branch, "status code: ", restrict_merges.status_code)
    add_access_key = requests.post(access_key_url, headers=bitbucket_header, auth=(bitbucket_auth_user, bitbucket_auth_password),
                                   data='{"key":"' + access_key + '","label":"Jenkins"}')
    print("access key addition status code : ", add_access_key.status_code)
    add_webhook = requests.post(hook_url, headers=bitbucket_header, auth=(bitbucket_auth_user, bitbucket_auth_password),
                                data='{"description":"Jenkins","url":"https://server-jenkins.com/bitbucket-hook/","active":"true","events":["repo:push"]}')
    print("webhook addition status code: ", add_webhook.status_code)

    # JENKINS PROVISION
    create_hook_job = requests.post(create_hook_job_url, headers=jenkins_header, data=create_hook_job_payload, auth=(jenkins_auth_user, jenkins_auth_password))
    print("jenkins hook job creation status code: ", create_hook_job.status_code)
    create_ms_develop_job = requests.post(create_develop_job_url, headers=jenkins_header, data=create_develop_job_payload, auth=(jenkins_auth_user, jenkins_auth_password))
    print("jenkins develop job creation status code: ", create_ms_develop_job.status_code)
    create_ms_staging_job = requests.post(create_staging_job_url, headers=jenkins_header, data=create_staging_job_payload, auth=(jenkins_auth_user, jenkins_auth_password))
    print("jenkins staging job creation status code: ", create_ms_staging_job.status_code)
    create_ms_master_job = requests.post(create_master_job_url, headers=jenkins_header, data=create_master_job_payload, auth=(jenkins_auth_user, jenkins_auth_password))
    print("jenkins master job creation status code: ", create_ms_master_job.status_code)

    build_jenkins_job = requests.post(build_url, headers=jenkins_header, auth=(jenkins_auth_user, jenkins_auth_password))
    print("job build status code: ", build_jenkins_job.status_code)

    # SLACK NOTIFICATIONS
    finish_notification = requests.post(send_message_url, headers=slack_header, data='{"channel":"' + slack_channel + '","text":"Repository and Pipeline is ready \n https://bitbucket.org/' + bitbucket_username + '/' + microservice_name + '"}')
    print("finish notification status code: ", finish_notification.status_code)
    db_user_creation_request = requests.post(send_message_url, headers=slack_header, data='{"channel":"' + dba_slack_channel + '","text":"Gengs, tulung buatkan database user `' + microservice_name + '` \n Beri pesan ini emoticon :DONE: jika sudah \n Thank you"}')
    print("db user creation request status code: ", db_user_creation_request.status_code)


ms_name = input("Insert new microservice name : ")
ns_name = input("Insert squad (for namespace) name : (please use \"default\" for now) ")
ms_framework = input("Type \"node\" for Integration API (NodeJS) or \"spring\" for Back-End (Spring Boot)  : ")

provisioner(ms_name, ns_name, ms_framework)
