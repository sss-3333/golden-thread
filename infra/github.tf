resource "azurerm_user_assigned_identity" "github" {
  name                = "id-golden-thread-github"
  location            = azurerm_resource_group.ai.location
  resource_group_name = azurerm_resource_group.ai.name
}

locals {
  github_repo = "repo:sss-3333@120253226/golden-thread@1450680240"
}

resource "azurerm_federated_identity_credential" "main" {
  name                      = "github-main"
  user_assigned_identity_id = azurerm_user_assigned_identity.github.id
  audience                  = ["api://AzureADTokenExchange"]
  issuer                    = "https://token.actions.githubusercontent.com"
  subject                   = "${local.github_repo}:ref:refs/heads/main"
}

resource "azurerm_federated_identity_credential" "pull_requests" {
  name                      = "github-pull-requests"
  user_assigned_identity_id = azurerm_user_assigned_identity.github.id
  audience                  = ["api://AzureADTokenExchange"]
  issuer                    = "https://token.actions.githubusercontent.com"
  subject                   = "${local.github_repo}:pull_request"
}

resource "azurerm_role_assignment" "github_openai" {
  scope                = azurerm_cognitive_account.ai.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_user_assigned_identity.github.principal_id
}