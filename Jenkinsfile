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
        sh 'pytest --cov-report term-missing --cov=nefila tests/ -k fortigate --junitxml test_fortigate.xml --junit_family=xunit2 --capture=no --verbose'
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