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
        sh 'env'
        sh 'pwd'
        sh 'ls'
        sh 'pytest   ./tests/test_fortigate.py::test_login_live -s -v --junitxml test_fortigate.xml '
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