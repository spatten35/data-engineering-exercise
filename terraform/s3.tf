resource "aws_s3_bucket" "open_library_dummy_bucket" {
  bucket = "open-library-dummy-bucket-${var.env}"
}

resource "aws_s3_bucket_ownership_controls" "ownership_controls" {
  bucket = aws_s3_bucket.open_library_dummy_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "open_library_acl" {
  depends_on = [aws_s3_bucket_ownership_controls.ownership_controls]
  bucket     = aws_s3_bucket.open_library_dummy_bucket.id
  acl        = "private"
}