resource "azurerm_user_assigned_identity" "pipeline" {
  name                = "id-golden-thread-pipeline"
  location            = azurerm_resource_group.ai.location
  resource_group_name = azurerm_resource_group.ai.name
}

resource "azurerm_role_assignment" "pipeline_openai" {
  scope                = azurerm_cognitive_account.ai.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_user_assigned_identity.pipeline.principal_id
}

output "pipeline_client_id" {
  value = azurerm_user_assigned_identity.pipeline.client_id
}
variable "aks_oidc_issuer" {
  type    = string
  default = ""
}

resource "azurerm_federated_identity_credential" "pipeline" {
  count                     = var.aks_oidc_issuer == "" ? 0 : 1
  name                      = "aks-pipeline"
  user_assigned_identity_id = azurerm_user_assigned_identity.pipeline.id
  audience                  = ["api://AzureADTokenExchange"]
  issuer                    = var.aks_oidc_issuer
  subject                   = "system:serviceaccount:golden-thread:pipeline"
}