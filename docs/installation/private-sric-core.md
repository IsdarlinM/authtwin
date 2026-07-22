# Private SRIC Core dependency

While repositories remain private, CI requires a fine-grained read token secret named `SRIC_READ_TOKEN` with access only to `sric-core`. Once `sric-core` is published through a trusted package/release channel, replace cross-repository checkout with the signed package dependency.
