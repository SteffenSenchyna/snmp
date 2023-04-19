#!/usr/bin/env groovy

pipeline {
  environment {
    CHART_VER = sh(script: "helm show chart ./helm-chart | grep '^version:' | awk '{print \$2}'", returnStdout: true).trim()
    BUILD_VER = "1.0.0"
    GIT_COMMIT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
    BUILD_TAG = "${BUILD_VER}-${GIT_COMMIT}"
    USER="ssenchyna"
    SERVICE = env.JOB_NAME.substring(0, env.JOB_NAME.lastIndexOf('/'))  
    }

  agent any

  stages {   
      stage("Docker login") {
        steps {
          sh """
            ## Login to Docker Repo ##
            echo $BUILD_TAG
            echo ${env.DOCKER_PASS} | docker login -u $USER --password-stdin
            echo ${env.DOCKER_PASS} | helm registry login registry-1.docker.io -u $USER --password-stdin 
          """
        }
      }

      stage("Clone Cluster Chart Repo and Build Image/Chart") {
        steps {
          // Clone the Git repository
          sh """
          docker build -t ${env.DOCKER_REPO}/$SERVICE:$BUILD_TAG .
          docker push ${env.DOCKER_REPO}/$SERVICE:$BUILD_TAG
          """
          dir('cluster-chart') {
                git branch: 'main', credentialsId: 'github-creds', url: 'https://github.com/SteffenSenchyna/cluster-chart.git'          
          }
          script {
            def CHART_VER_DEV = sh(script: "helm show chart ./cluster-chart/dev/ | grep '^version:' | awk '{print \$2}'", returnStdout: true).trim()
            if (CHART_VER_DEV != CHART_VER) {
              sh """
              yq eval '(.dependencies[] | select (.name == strenv(SERVICE))).version = strenv(CHART_VER)' -i ./dev/Chart.yaml
              yq eval \'.[env(SERVICE)].image.tag = env(BUILD_TAG)\' -i ./cluster-chart/dev/values.yaml 
              helm package ./helm-chart
              helm push "$SERVICE-$CHART_VER".tgz oci://registry-1.docker.io/$USER
              """
              withCredentials([gitUsernamePassword(credentialsId: 'github-creds', gitToolName: 'Default')]) {
                  sh """
                  cd cluster-chart
                  yq eval \'.[env(SERVICE)].image.tag = env(BUILD_TAG)\' ./dev/values.yaml -i
                  git add .
                  git commit -m "${SERVICE}:${BUILD_TAG} Chart:${CHART_VER}"
                  git push -u origin main
                  """
              } 
          } else{
              withCredentials([gitUsernamePassword(credentialsId: 'github-creds', gitToolName: 'Default')]) {
                  sh """
                  cd cluster-chart
                  yq eval \'.[env(SERVICE)].image.tag = env(BUILD_TAG)\' ./dev/values.yaml -i
                  git add .
                  git commit -m "${SERVICE}:${BUILD_TAG}"
                  git push -u origin main
                  """
          }
        }
      }
    }
  }
}
    post {
    always {
        sh 'if [ -n "$(find . -maxdepth 1 -name "*.tgz")" ]; then rm ./*.tgz; fi'
        sh 'if [ -d "cluster-chart" ]; then rm -r cluster-chart; fi'
    }
  }
}