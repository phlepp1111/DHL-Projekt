provider "aws" {
  region = "eu-central-1"  # Ihre gewünschte Region
}

##################################VPC#############################################

#VPC
resource "aws_vpc" "my_vpc" {
  cidr_block = "10.0.0.0/16"
}

#IGW
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.my_vpc.id

  tags = {
    Name = "internet_gateway"
  }
}

#Route for Table
resource "aws_route" "public_route" {
  route_table_id         = aws_route_table.public_route_table.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.gw.id
}


# Routen-Tabelle-Zuordnung für Subnetz 1A
resource "aws_route_table_association" "public_route_table_association_1a" {
  subnet_id      = aws_subnet.public_subnet1a.id
  route_table_id = aws_route_table.public_route_table.id
}

# Routen-Tabelle-Zuordnung für Subnetz 1B
resource "aws_route_table_association" "public_route_table_association_1b" {
  subnet_id      = aws_subnet.public_subnet1b.id
  route_table_id = aws_route_table.public_route_table.id
}



#Route Table
resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.my_vpc.id

  tags = {
    Name = "public_route_table"
  }
}

#Subnetz
resource "aws_subnet" "public_subnet1a" {
  vpc_id     = aws_vpc.my_vpc.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "eu-central-1a"  # Ihre gewünschte Verfügbarkeitszone
  # map_public_ip_on_launch = true  # Enable public IP assignment
}

resource "aws_subnet" "private_subnet1a" {
  vpc_id     = aws_vpc.my_vpc.id
  cidr_block = "10.0.2.0/24"
  availability_zone = "eu-central-1a"  # Ihre gewünschte Verfügbarkeitszone
}



resource "aws_subnet" "public_subnet1b" {
  vpc_id     = aws_vpc.my_vpc.id
  cidr_block = "10.0.3.0/24"
  availability_zone = "eu-central-1b"  # Ihre gewünschte Verfügbarkeitszone
  # map_public_ip_on_launch = true  # Enable public IP assignment
}

resource "aws_subnet" "private_subnet1b" {
  vpc_id     = aws_vpc.my_vpc.id
  cidr_block = "10.0.4.0/24"
  availability_zone = "eu-central-1b"  # Ihre gewünschte Verfügbarkeitszone
}

#Route Table für Private Subnetze
resource "aws_route_table" "private_route_table1a" {
  vpc_id = aws_vpc.my_vpc.id
}

resource "aws_route_table_association" "private_subnet1a" {
  subnet_id      = aws_subnet.private_subnet1a.id
  route_table_id = aws_route_table.private_route_table1a.id
}

resource "aws_route_table" "private_route_table1b" {
  vpc_id = aws_vpc.my_vpc.id
}

resource "aws_route_table_association" "private_subnet1b" {
  subnet_id      = aws_subnet.private_subnet1b.id
  route_table_id = aws_route_table.private_route_table1b.id
}


############################DynamoDB############################

resource "aws_dynamodb_table" "OrderDB" {
  name           = "Orders"
  hash_key = "packageID"
  read_capacity = 20
  write_capacity = 20

  attribute {
    name = "packageID"
    type = "S"
  }
}

# VPC Endpoint DynamoDB
resource "aws_vpc_endpoint" "dynamodb_endpoint" {
  vpc_id       = aws_vpc.my_vpc.id
  service_name = "com.amazonaws.eu-central-1.dynamodb"
  vpc_endpoint_type = "Gateway"

  # Nur private Subnetze sollen Zugriff haben
  route_table_ids = [
    aws_route_table.private_route_table1a.id,
    aws_route_table.private_route_table1b.id,
  ]
}

###################################################