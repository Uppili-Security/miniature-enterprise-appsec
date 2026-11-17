
resource "aws_s3_bucket" "demo_bucket" {
  bucket = "miniature-enterprise-appsec-demo-bucket"
}

resource "aws_s3_bucket_acl" "demo_bucket_acl" {
  bucket = aws_s3_bucket.demo_bucket.id
  acl    = "public-read"
}
