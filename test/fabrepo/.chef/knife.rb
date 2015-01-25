cookbook_path    ["cookbooks", "dev-cookbooks", "site-cookbooks"]
node_path        "nodes"
role_path        "roles"
environment_path "environments"
data_bag_path    "data_bags"
encrypted_data_bag_secret ".chef/data_bag_key"
http_proxy       "localhost"
https_proxy      "localhost"

knife[:berkshelf_path] = "cookbooks"

# for chef-server
USER = ENV["USER"]
PWD = ENV["PWD"]
node_name        USER
chef_server_url  "https://192.168.254.129"
client_key       "#{PWD}/.chef/#{USER}.pem"
validation_key   "#{PWD}/.chef/chef-validator.pem"

