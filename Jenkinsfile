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
        sh 'pytest --cov-report term-missing --cov=nefila tests/ -k fortigate --junitxml test_fortigate.xml --capture=no --verbose'
      }
    }

  }
  post {
    always {
      junit 'test_fortigate.xml'
    }

  }
}