# The reason to split the following handlers
# is that we want to separetly specify each key_prefix on S3.
from smtools.torch.handlers.archive import archive
from smtools.torch.handlers.s3_copy import s3_copy
from smtools.torch.handlers.s3_copy import remove
