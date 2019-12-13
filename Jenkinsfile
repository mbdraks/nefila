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
        NEFILA_PASSWORD = 'fortinet'
      }
      steps {
        sh 'pytest tests/test_fortigate.py -v --junitxml test_fortigate.xml'
      }
    }

  }
  post {
    always {
      junit 'test_fortigate.xml'
    }

  }
}