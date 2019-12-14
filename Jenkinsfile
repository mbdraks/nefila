pipeline {
  agent {
    docker {
      image 'python:3.7.2'
    }

  }
  stages {
    stage('build') {
      steps {
        sh 'pip install pipenv'
        sh 'pipenv lock'
        sh 'pipenv install --dev --system --deploy'
      }
    }

    stage('testing') {
      environment {
        FORTIGATE_HOSTNAME = '10.20.10.15'
        NEFILA_USERNAME = 'admin'
        NEFILA_PASSWORD = ''
      }
      steps {
        sh 'pytest  --junitxml test_fortigate.xml --capture=no -k fortigate'
      }
    }

    stage('results') {
      steps {
        junit(allowEmptyResults: true, testResults: '*.xml')
      }
    }

  }
  post {
    always {
      junit 'test_fortigate.xml'
    }

  }
}