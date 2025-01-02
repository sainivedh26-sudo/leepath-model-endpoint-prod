[build]
  command = "pip install -r requirements.txt"
  functions = "netlify/functions"

[functions]
  node_bundler = "esbuild"
  external_node_modules = ["numpy", "pandas", "networkx", "scikit-learn", "joblib"]

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
