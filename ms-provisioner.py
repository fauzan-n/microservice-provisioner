# Provision repository on Bitbucket, and create pipeline on Jenkins using Rest API

import requests
import os

bitbucket_api_url = "https://api.bitbucket.org/2.0"
bitbucket_username = ""                                 # BITBUCKET REPOSITORY OWNER NAME
bitbucket_auth_user = ""                                # BITBUCKET USERNAME
bitbucket_auth_password = os.environ[""]                # BITBUCKET PASSWORD
bitbucket_header = {'Content-Type': 'application/json'}
jenkins_api_url = ""                                    # JENKINS SERVER URL
jenkins_auth_user = ""                                  # JENKINS USERNAME
jenkins_auth_password = os.environ[""]                  # JENKINS PASSWORD
jenkins_header = {'Content-Type': 'text/xml'}


def ms_bootstrap(microservice_name):

    repository_url = bitbucket_api_url + "/repositories/" + bitbucket_username + "/" + microservice_name
    commit_url = repository_url + "/src"
    branch_url = repository_url + "/refs/branches"
    branch_restriction_url = repository_url + "/branch-restrictions"
    access_key_url = repository_url + "/deploy-keys"
    hook_url = repository_url + "/hooks"
    create_job_url = jenkins_api_url + "/job/microservices-pipelines/createItem?name=" + microservice_name
    create_job_payload = """<?xml version='1.1' encoding='UTF-8'?><flow-definition plugin="workflow-job@2.31"><actions/><description></description><keepDependencies>false</keepDependencies><properties><org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty><triggers><com.cloudbees.jenkins.plugins.BitBucketTrigger plugin="bitbucket@1.1.9"><spec></spec></com.cloudbees.jenkins.plugins.BitBucketTrigger></triggers></org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty></properties><definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.63"><scm class="hudson.plugins.git.GitSCM" plugin="git@3.9.3"><configVersion>2</configVersion><userRemoteConfigs><hudson.plugins.git.UserRemoteConfig><url>git@bitbucket.org:investree/{{MS-NAME}}</url><credentialsId>private-key-for-bitbucket</credentialsId></hudson.plugins.git.UserRemoteConfig></userRemoteConfigs><branches><hudson.plugins.git.BranchSpec><name>*/master</name></hudson.plugins.git.BranchSpec><hudson.plugins.git.BranchSpec><name>*/staging</name></hudson.plugins.git.BranchSpec><hudson.plugins.git.BranchSpec><name>*/develop</name></hudson.plugins.git.BranchSpec></branches><doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations><submoduleCfg class="list"/><extensions/></scm><scriptPath>Jenkinsfile</scriptPath><lightweight>false</lightweight></definition><triggers/><disabled>false</disabled></flow-definition>"""
    build_url = jenkins_api_url + "/job/microservices-pipelines/job/" + microservice_name + "/build"

    # BITBUCKET PROVISION
    create_repository = requests.post(repository_url, headers=bitbucket_header, data="""{"is_private":"true","project":{"key":"COR"}}""",
                                      auth=(bitbucket_auth_user, bitbucket_auth_password))
    print("repository creation status code : ", create_repository.status_code)
    initial_commit = requests.post(commit_url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data='created from API',
                                   auth=(bitbucket_auth_user, bitbucket_auth_password))
    print("initial commit status code: ", initial_commit.status_code)
    branches = ["staging", "develop", "feature/devops"]
    for branch in branches:
        create_branches = requests.post(branch_url, headers=bitbucket_header, data='{"name":"' + branch + '","target":{"hash":"master"}}',
                                        auth=(bitbucket_auth_user, bitbucket_auth_password))
        print(branch, "branch creation status code : ", create_branches.status_code)
    branches.append("master")
    branches.remove("feature/devops")
    restriction_rules = ["delete", "force", "push"]
    for branch in branches:
        for rule in restriction_rules:
            restrict_branches = requests.post(branch_restriction_url, headers=bitbucket_header, auth=(bitbucket_auth_user, bitbucket_auth_password),
                                              data='{"kind":"' + rule + '","pattern":"' + branch + '","groups":[],"users":[]}')
            print(rule, "rule creation on ", branch, " branch status code: ", restrict_branches.status_code)
        restrict_merges = requests.post(branch_restriction_url, headers=bitbucket_header, auth=(bitbucket_auth_user, bitbucket_auth_password),
                                        data='{"kind":"restrict_merges","pattern":"' + branch + '","groups":[{"owner":{"username":"investree"},"slug":"devops"},{"owner":{"username":"investree"},"slug":"coretree-backend-developers"}],"users":[]}')
        print("restrict merges rule creation on branch", branch, "status code: ", restrict_merges.status_code)
    add_access_key = requests.post(access_key_url, headers=bitbucket_header, auth=(bitbucket_auth_user, bitbucket_auth_password),
                                   data='{"key":"'ssh-key'","label":"Jenkins"}')
    print("access key addition status code : ", add_access_key.status_code)
    add_webhook = requests.post(hook_url, headers=bitbucket_header, auth=(bitbucket_auth_user, bitbucket_auth_password),
                                data='{"description":"Jenkins","url":"'jenkins_api_url',/bitbucket-hook/","active":"true","events":["repo:push"]}')
    print("webhook addition status code: ", add_webhook.status_code)

    # JENKINS PROVISION
    create_jenkins_job = requests.post(create_job_url, headers=jenkins_header, data=create_job_payload, auth=(jenkins_auth_user, jenkins_auth_password))
    print("jenkins job creation status code: ", create_jenkins_job.status_code)
    build_jenkins_job = requests.post(build_url, headers=jenkins_header, auth=(jenkins_auth_user, jenkins_auth_password))
    print("job build status code: ", build_jenkins_job.status_code)


ms_bootstrap(input("Insert new microservice name : "))
