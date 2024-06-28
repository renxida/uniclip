-- Uniclip NeoVim LUA client

-- Configuration
local config_path = vim.fn.expand('~/.config/uniclip/config.yaml')
local poll_interval = 500 -- milliseconds
local max_backoff = 64000 -- maximum backoff time in milliseconds
local log_file = vim.fn.expand('/tmp/uniclip_log.txt')
local max_log_size = 1000000 -- 1MB

local M = {}

-- Utility functions

-- Load configuration from file
local function load_config()
  local f = io.open(config_path, "r")
  if f then
    local content = f:read("*all")
    f:close()
    local group_id = content:match("group_id:%s*(.-)%s*\n")
    local server_address = content:match("server_address:%s*(.-)%s*\n")
    return group_id, server_address
  end
  error("Failed to load Uniclip configuration")
end

-- Log error messages
local function log_error(message)
  local f = io.open(log_file, "a")
  if f then
    f:write(os.date("%Y-%m-%d %H:%M:%S") .. " - " .. message .. "\n")
    f:close()
    
    -- Check file size and truncate if necessary
    local size = vim.fn.getfsize(log_file)
    if size > max_log_size then
      local temp_file = log_file .. ".temp"
      os.execute("tail -c " .. max_log_size / 2 .. " " .. log_file .. " > " .. temp_file .. " && mv " .. temp_file .. " " .. log_file)
    end
  end
end

-- Make HTTP request
local function make_request(method, url, body)
  local curl_command = string.format(
    "curl -s -X %s -H 'Content-Type: application/json' %s '%s'",
    method,
    body and string.format("-d '%s'", vim.fn.shellescape(body)) or "",
    url
  )
  local handle = io.popen(curl_command)
  local result = handle:read("*a")
  handle:close()
  return result
end

-- Hash content
local function hash_content(content)
  return vim.fn.sha256(content)
end

-- Get current timestamp
local function get_timestamp()
  return os.time()
end

-- Send content to server
function M.send_to_server(content, timestamp)
  local group_id, server_address = load_config()
  local temp_file = os.tmpname()
  
  local f = io.open(temp_file, "w")
  if not f then
    log_error("Failed to create temporary file")
    return
  end
  f:write(vim.fn.json_encode({
    group_id = group_id,
    client_id = "neovim-client",
    content = content,
    timestamp = timestamp
  }))
  f:close()

  local curl_command = string.format(
    "curl -s -X POST -H 'Content-Type: application/json' -d '@%s' '%s/update'",
    temp_file,
    server_address
  )

  local handle = io.popen(curl_command .. " 2>&1")
  local result = handle:read("*a")
  local success, exit_type, exit_code = handle:close()
  
  os.remove(temp_file)

  if not success then
    log_error("Failed to send update to server. Exit type: " .. tostring(exit_type) .. ", Exit code: " .. tostring(exit_code))
    log_error("Command output: " .. result)
  elseif not result:match('"status":"updated"') then
    log_error("Server response doesn't indicate success. Response: " .. result)
  end
end

-- Receive content from server
function M.receive_from_server(content_hash, timestamp)
  local group_id, server_address = load_config()
  local url = string.format("%s/poll/%s/neovim-client?hash=%s&timestamp=%d", server_address, group_id, content_hash, timestamp)
  local response = make_request("GET", url)
  local success, data = pcall(vim.fn.json_decode, response)
  if not success then
    log_error("Failed to decode server response: " .. response)
    return nil
  end
  return data
end

-- Clipboard sync functions

local last_clipboard = ""
local last_timestamp = 0
local current_backoff = poll_interval

-- Update clipboard with exponential backoff
local function update_clipboard()
  local content_hash = hash_content(last_clipboard)
  local data = M.receive_from_server(content_hash, last_timestamp)
  if data then
    if data.status == "update_needed" then
      if data.content ~= last_clipboard then
        vim.fn.setreg('"', data.content)
        last_clipboard = data.content
        last_timestamp = data.timestamp
      end
    end
    current_backoff = poll_interval -- Reset backoff on successful poll
  else
    log_error("Failed to receive update from server. Retrying in " .. current_backoff / 1000 .. " seconds.")
    current_backoff = math.min(current_backoff * 2, max_backoff) -- Exponential backoff
  end
end

-- Start background polling
local function start_background_poll()
  local timer = vim.loop.new_timer()
  timer:start(0, current_backoff, vim.schedule_wrap(function()
    update_clipboard()
    timer:set_repeat(current_backoff) -- Update the timer interval
  end))
end

-- Setup function
function M.setup()
  vim.opt.clipboard = "unnamedplus"

  vim.api.nvim_create_autocmd("TextYankPost", {
    group = vim.api.nvim_create_augroup("Uniclip", { clear = true }),
    callback = function()
      local yanked_text = table.concat(vim.v.event.regcontents, "\n")
      local timestamp = get_timestamp()
      M.send_to_server(yanked_text, timestamp)
      last_clipboard = yanked_text
      last_timestamp = timestamp
    end,
  })

  vim.keymap.set('n', 'p', function()
    local content_hash = hash_content(last_clipboard)
    local data = M.receive_from_server(content_hash, last_timestamp)
    if data and data.status == "update_needed" and data.content ~= last_clipboard then
      vim.fn.setreg('"', data.content)
      last_clipboard = data.content
      last_timestamp = data.timestamp
    end
    return 'p'
  end, { expr = true })

  start_background_poll()
end

-- Function to check Uniclip status
function M.check_status()
  local group_id, server_address = load_config()
  local content_hash = hash_content(last_clipboard)
  local response = make_request("GET", string.format("%s/poll/%s/neovim-client?hash=%s&timestamp=%d", server_address, group_id, content_hash, last_timestamp))
  local success, data = pcall(vim.fn.json_decode, response)
  if success and data then
    print("Uniclip server is running and reachable.")
    print("Server address: " .. server_address)
    print("Group ID: " .. group_id)
    print("Current backoff: " .. current_backoff / 1000 .. " seconds")
    print("Last clipboard content hash: " .. content_hash)
    print("Last clipboard timestamp: " .. os.date("%Y-%m-%d %H:%M:%S", last_timestamp))
    print("Server response: " .. vim.inspect(data))
  else
    print("Unable to reach Uniclip server or server is not responding correctly.")
    print("Server address: " .. server_address)
    print("Group ID: " .. group_id)
    print("Current backoff: " .. current_backoff / 1000 .. " seconds")
    print("Last clipboard content hash: " .. content_hash)
    print("Last clipboard timestamp: " .. os.date("%Y-%m-%d %H:%M:%S", last_timestamp))
    print("Server response: " .. vim.inspect(response))
  end
end

-- Function to display log
function M.display_log()
  local f = io.open(log_file, "r")
  if f then
    local content = f:read("*all")
    f:close()
    if #content > 0 then
      vim.cmd("new")
      vim.api.nvim_buf_set_lines(0, 0, -1, false, vim.split(content, "\n"))
      vim.bo.buftype = "nofile"
      vim.bo.bufhidden = "wipe"
      vim.bo.swapfile = false
      vim.bo.filetype = "uniclip_log"
    else
      print("Uniclip log is empty.")
    end
  else
    print("Unable to open Uniclip log file.")
  end
end

-- Command to interact with Uniclip
vim.api.nvim_create_user_command("Uniclip", function(opts)
  if opts.args == "status" then
    M.check_status()
  elseif opts.args == "log" then
    M.display_log()
  else
    print("Unknown Uniclip command. Available commands: status, log")
  end
end, {
  nargs = '?',
  complete = function(_, _, _)
    return { "status", "log" }
  end,
})

return M