-- Uniclip NeoVim LUA client
-- this depends on having a ~/.config/uniclip/config.yaml file with the following format:
-- group_id: <group_id>
-- server_address: <server_address>

local M = {}

-- Configuration
local config_path = vim.fn.expand('~/.config/uniclip/config.yaml')
local poll_interval = 1000 -- milliseconds

-- Utility functions
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

function M.send_to_server(content)
  local group_id, server_address = load_config()
  local body = vim.fn.json_encode({
    group_id = group_id,
    client_id = "neovim-client",
    content = content
  })
  local curl_command = string.format(
    "curl -s -X POST -H 'Content-Type: application/json' -d '%s' '%s/update'",
    vim.fn.shellescape(body),
    server_address
  )
  local handle = io.popen(curl_command .. " 2>&1")
  local result = handle:read("*a")
  local success, exit_type, exit_code = handle:close()
  
  if success then
    if result:match('"status":"updated"') then
      print("Sent update to server successfully")
    else
      print("Server response doesn't indicate success. Response: " .. result)
    end
  else
    print("Failed to send update to server. Exit type: " .. tostring(exit_type) .. ", Exit code: " .. tostring(exit_code))
    print("Command output: " .. result)
  end
  
  -- Log the curl command for debugging
  vim.fn.writefile({curl_command}, vim.fn.expand("~/.uniclip_debug.log"), "a")
end


function M.receive_from_server()
  local group_id, server_address = load_config()
  local response = make_request("GET", server_address .. "/poll/" .. group_id .. "/neovim-client")
  local data = vim.fn.json_decode(response)
  return data and data.content
end

-- Clipboard sync functions
local last_clipboard = ""

local function update_clipboard()
  local content = M.receive_from_server()
  if content and content ~= last_clipboard then
    vim.fn.setreg('"', content)
    last_clipboard = content
    print("Clipboard updated from server")
  end
end

local function start_background_poll()
  local timer = vim.loop.new_timer()
  timer:start(0, poll_interval, vim.schedule_wrap(function()
    update_clipboard()
  end))
end

-- Setup function
function M.setup()
  -- Set clipboard to use external tool
  vim.opt.clipboard = "unnamedplus"

  -- Set up autocmd to sync clipboard
  vim.api.nvim_create_autocmd("TextYankPost", {
    group = vim.api.nvim_create_augroup("Uniclip", { clear = true }),
    callback = function()
      local yanked_text = table.concat(vim.v.event.regcontents, "\n")
      M.send_to_server(yanked_text)
      last_clipboard = yanked_text
    end,
  })

  -- Override default paste command
  vim.keymap.set('n', 'p', function()
    local content = M.receive_from_server()
    if content and content ~= last_clipboard then
      vim.fn.setreg('"', content)
      last_clipboard = content
    end
    return 'p'
  end, { expr = true })

  -- Start background polling
  start_background_poll()
end

return M
