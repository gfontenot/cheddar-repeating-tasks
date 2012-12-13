require 'sinatra'
require 'redis'
require 'json'
require 'net/http'

get '/' do
  @title = "Cheddar Repeating Tasks"
  if logged_in
    redirect '/home'
  else
    erb :login
  end
end

get '/home' do
  erb :home
end

get '/tasks' do
  @@bearer
end

get '/login' do
  cheddar_auth_api = 'https://api.cheddarapp.com/oauth/authorize'
  redirect "#{cheddar_auth_api}?client_id=#{ENV['CHEDDAR_CLIENT_ID']}"
end

get '/auth_callback' do
  code = params[:code]
  user = cheddar_access_token_for_code code
  @@bearer = user.to_s
  redirect '/tasks'
end

private

def logged_in
  false
end

def cheddar_access_token_for_code code
  cheddar_api = URI.parse('https://api.cheddarapp.com/oauth/token')
  https = Net::HTTP.new(cheddar_api.host, cheddar_api.port)
  https.use_ssl = true
  request = Net::HTTP::Post.new(cheddar_api.path)
  request.basic_auth 'ec0138a5ca7c328cb6430172935ecbfd', '45e7b7d7bf653259fe40b9b99ad74a04'
  # request.basic_auth ENV['CHEDDAR_CLIENT_ID'], ENV['CHEDDAR_CLIENT_SECRET']
  request.body = "grant_type=authorization_code&code=#{code}"
  response = https.request(request)
  JSON.parse(response.body)
end

__END__

@@ layout
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title><%= @title %></title>
  <link rel="stylesheet" href="/reset.css" type="text/css" media="all" charset="utf-8">
  <link rel="stylesheet" href="/style.css" type="text/css" media="all" charset="utf-8">
</head>
<body>
  <div id="content">
    <%= yield %>
  </div>
</body>
</html>

@@ login
<a href="/login">Log in with Cheddar</a>

@@ home
<h1>Logged In!!</h1>
