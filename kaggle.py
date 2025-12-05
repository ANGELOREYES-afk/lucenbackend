import kagglehub

# Download latest version
path = kagglehub.dataset_download("alexanderxela/sp-500-companies")

print("Path to dataset files:", path)