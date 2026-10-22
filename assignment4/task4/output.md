siddeshnatesan@Siddeshs-MacBook-Pro ~ % ollama --version
ollama version is 0.40.8
siddeshnatesan@Siddeshs-MacBook-Pro ~ % curl http://localhost:11434/api/version
{"version":"0.40.8"}%                                                                                                                                                                                                siddeshnatesan@Siddeshs-MacBook-Pro ~ % ollama pull qwen2.5:1.5b-instruct-q4_K_M
pulling manifest 
pulling 183715c43589: 100% ▕███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▏ 986 MB                         
pulling 377ac4d7aeef: 100% ▕███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▏  487 B                         
verifying sha256 digest 
writing manifest 
success 
siddeshnatesan@Siddeshs-MacBook-Pro ~ % ollama list
NAME                            ID              SIZE      MODIFIED      
qwen2.5:1.5b-instruct-q4_K_M    65ec06548149    986 MB    2 seconds ago    
siddeshnatesan@Siddeshs-MacBook-Pro ~ % curl http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:1.5b-instruct-q4_K_M",
    "messages": [
      {
        "role": "user",
        "content": "Reply with exactly READY."
      }
    ],
    "stream": false,
    "options": {
      "temperature": 0,
      "seed": 42
    }
  }'
{"model":"qwen2.5:1.5b-instruct-q4_K_M","created_at":"2026-10-22T23:02:01.276318Z","message":{"role":"assistant","content":"READY"},"done":true,"done_reason":"stop","total_duration":1066559500,"load_duration":800551416,"prompt_eval_count":34,"prompt_eval_cached_count":0,"prompt_eval_duration":252998000,"eval_count":2,"eval_duration":9623000}%                                                                                  siddeshnatesan@Siddeshs-MacBook-Pro ~ % 
siddeshnatesan@Siddeshs-MacBook-Pro ~ % 
siddeshnatesan@Siddeshs-MacBook-Pro ~ % 
siddeshnatesan@Siddeshs-MacBook-Pro ~ % 
siddeshnatesan@Siddeshs-MacBook-Pro ~ % curl http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:1.5b-instruct-q4_K_M",
    "messages": [
      {
        "role": "user",
        "content": "Reply with exactly READY."
      }
    ],
    "stream": false,
    "options": {
      "temperature": 0,
      "seed": 42
    }
  }'
{"model":"qwen2.5:1.5b-instruct-q4_K_M","created_at":"2026-10-22T23:02:22.315322Z","message":{"role":"assistant","content":"READY"},"done":true,"done_reason":"stop","total_duration":34593167,"load_duration":1692708,"prompt_eval_count":34,"prompt_eval_cached_count":33,"prompt_eval_duration":21263000,"eval_count":2,"eval_duration":9411000}%                                                                                      siddeshnatesan@Siddeshs-MacBook-Pro ~ % 

