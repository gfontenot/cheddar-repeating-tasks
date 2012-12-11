require 'net/http'

module Cheddar
  class TaskCreator
    def initialize(text)
      cheddar_api = URI.parse('https://api.cheddarapp.com/v1/lists/52514/tasks')
      https = Net::HTTP.new(cheddar_api.host, cheddar_api.port)
      https.use_ssl = true
      request = Net::HTTP::Post.new(cheddar_api.path)
      request.body = "task[text]=#{URI.escape(text)}"
      request['Authorization'] = "Bearer #{ENV['CHEDDAR_BEARER_TEST']}"
      https.request(request)
    end
  end
end
