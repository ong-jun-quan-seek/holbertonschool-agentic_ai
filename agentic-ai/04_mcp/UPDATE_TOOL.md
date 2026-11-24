# 2. Engineer Mode (Developing a New MCP Tool)

## Name of the added Tool 

`update_customer_status`

## Parameters sent during the test

Email: dev@entreprise.com
Status: Inactive

## Confirmation of the verification performed

Short confirmation as Human-in-the-Loop control below was asked before authorizing the call.

``` 
{ "email": "dev@entreprise.com", "new_status": "Inactive" }
```

This was the output
`Customer status updated for dev@entreprise.com`

Final message 
`Updated dev@entreprise.com to Inactive.`
