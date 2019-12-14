pipeline {
  agent {
    docker {
      image 'ee6cfd6608af'
    }

  }
  stages {
    stage('build') {
      steps {
        echo 'go!'
      }
    }

    stage('testing') {
      environment {
        FORTIGATE_HOSTNAME = '10.20.10.15'
        NEFILA_USERNAME = 'admin'
        NEFILA_PASSWORD = 'fortinet'
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