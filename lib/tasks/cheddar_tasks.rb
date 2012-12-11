require 'net/http'
require 'redis'
require 'json'

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

  class TaskCollector
    def initialize
      redis_uri = URI.parse(ENV['REDISTOGO_URL'])
      @redis = Redis.new(host: redis_uri.host, port: redis_uri.port, password: redis_uri.password)
    end

    def tasks
      tasks_json = @redis.smembers('tasks')
      tasks = tasks_json.map { |t_json| JSON.parse(t_json) }
      tasks.select { |t| t['day_of_month'] == 25 }
    end
  end
end
