provider "aws" {
  region = "eu-central-1"  
}

#############################Lambda##################################

resource "aws_lambda_function" "get_driver" {
  function_name = "getdriverlambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "index.lambda_handler" 
  runtime       = "python3.9"  
  

  filename = "./getdriver/index.zip"
}

resource "aws_lambda_event_source_mapping" "dynamodb_event_source" {
  event_source_arn = aws_dynamodb_table.OrderDB.stream_arn
  function_name = aws_lambda_function.get_driver.arn
  starting_position          = "LATEST"

  filter_criteria {
    filter {
      pattern = jsonencode({
        eventName = ["INSERT"],
        eventSource = ["aws:dynamodb"]
      })
    }
  }
}


resource "aws_lambda_function" "orderput" {
  function_name = "orderlambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "orderlambda.lambda_handler" 
  runtime       = "python3.9"  

  filename = "./python/orderlambda.zip"

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.OrderDB.name
      SQS_QUEUE_URL  = aws_sqs_queue.order_queue.id
    }
  }
}
resource "aws_lambda_function" "driverput" {
  function_name = "driverlambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "addDrivers.lambda_handler" 
  runtime       = "python3.9"  

  filename = "./python/addDrivers.zip"

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.DriverDB.name
      
    }
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy_attachment" "lambda_exec_policy" {
  name = "Lambda-exec"
  policy_arn = aws_iam_policy.lambda_policy.arn
  roles      = [aws_iam_role.lambda_exec_role.name]
}
resource "aws_iam_policy_attachment" "sqs_exec_policy" {
  name = "Lambda-SQS"
  policy_arn = aws_iam_policy.sqs_policy.arn
  roles      = [aws_iam_role.lambda_exec_role.name]
}

resource "aws_iam_policy" "lambda_policy" {
  name = "lambda-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action   = ["dynamodb:*"],
      Effect   = "Allow",
      Resource = "*"
    },
    {
    Action = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ],
    Effect = "Allow",
    Resource = "*"
    }
    
    ]
  })
}




############################DynamoDB############################

resource "aws_dynamodb_table" "OrderDB" {
  name           = "Orders"
  hash_key = "packageID"
  read_capacity = 20
  write_capacity = 20

  #stream aktivieren
  stream_view_type = "NEW_IMAGE"
  stream_enabled   = true

  attribute {
    name = "packageID"
    type = "S"
  }
}

resource "aws_dynamodb_table" "DriverDB" {
  name           = "Drivers"
  hash_key = "driverID"
  read_capacity = 20
  write_capacity = 20

  #stream aktivieren
  stream_view_type = "NEW_IMAGE"
  stream_enabled   = true

  attribute {
    name = "driverID"
    type = "S"
  }
}
###################################################

###################SQS#############################
resource "aws_sqs_queue" "order_queue" {
  name                        = "order-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
}

resource "aws_iam_policy" "sqs_policy" {
  name = "sqs-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:GetQueueUrl",
        ],
        Effect   = "Allow",
        Resource = aws_sqs_queue.order_queue.arn,
      },
    ],
  })
}
###################################################