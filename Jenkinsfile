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
      steps {
        sh 'pytest tests/test_fortigate.py -v'
      }
    }

  }
}