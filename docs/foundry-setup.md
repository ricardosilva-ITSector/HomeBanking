# Azure AI Foundry Setup Guide for HomeBanking Agent

This guide walks through setting up Azure AI Foundry prerequisites for the HomeBanking transfer copilot agent.

**Estimated time**: 20-30 minutes  
**Prerequisites**: Azure subscription with appropriate permissions

---

## Overview

To run the HomeBanking agent, you need:
1. An Azure AI Foundry project
2. A deployed language model (e.g., gpt-4o, gpt-4.1, o1)
3. Proper authentication configured
4. Configuration values copied to `.env`

---

## Step 1: Create Azure AI Foundry Project

### Option A: Azure Portal (Recommended for First-Time Users)

1. **Navigate to Azure AI Foundry Portal**
   - Go to [https://ai.azure.com](https://ai.azure.com)
   - Sign in with your Azure credentials
   - Toggle to **New Foundry** experience (if available)

2. **Create a New Project**
   - Click **+ New project** or **Create project**
   - Fill in project details:
     - **Project name**: `homebanking-agent` (or your preferred name)
     - **Subscription**: Select your Azure subscription
     - **Resource group**: Create new or select existing
     - **Region**: Choose a region that supports your desired model (recommended: `East US 2`, `Sweden Central`, or `West US`)
   - Click **Create**

3. **Wait for Provisioning**
   - Project creation takes 2-5 minutes
   - Azure provisions: Foundry resource, Azure AI Search, Storage account, Key Vault

4. **Note Your Project Endpoint**
   - After creation, go to **Project settings** → **Properties**
   - Copy the **Project endpoint** (format: `https://your-resource.ai.azure.com/api/projects/your-project`)
   - Save this for later

### Option B: Azure CLI

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "<your-subscription-id>"

# Create resource group
az group create \
  --name homebanking-rg \
  --location eastus2

# Create AI Foundry resource (Cognitive Services account)
az cognitiveservices account create \
  --name homebanking-foundry \
  --resource-group homebanking-rg \
  --kind AIServices \
  --sku S0 \
  --location eastus2 \
  --yes

# Get the endpoint
az cognitiveservices account show \
  --name homebanking-foundry \
  --resource-group homebanking-rg \
  --query properties.endpoint \
  --output tsv
```

---

## Step 2: Deploy a Language Model

### Recommended Models for Transfer Copilot

| Model | Best For | Region Availability | Notes |
|-------|----------|---------------------|-------|
| **gpt-4o** | Production readiness, balanced performance | Most regions | Recommended for MVP |
| **gpt-4.1** | Latest capabilities | Limited regions | If available in your region |
| **gpt-4.1-mini** | Cost-effective, fast | Most regions | Good for development/testing |
| **o1** | Complex reasoning | Limited regions | Overkill for transfer use case |

### Deploy via Azure Portal

1. **Navigate to Your Project**
   - Go to [https://ai.azure.com](https://ai.azure.com)
   - Select your project

2. **Open Model Catalog**
   - Click **Build** → **Deployments**
   - Or click **+ Create deployment**

3. **Select Model**
   - Search for `gpt-4o` (or your preferred model)
   - Click **Deploy**

4. **Configure Deployment**
   - **Deployment name**: `gpt-4o-deployment` (you'll use this in .env)
   - **Model version**: Select latest
   - **Deployment type**: Standard
   - **Tokens per minute (TPM)**: Start with 10K (adjust based on usage)
   - Click **Deploy**

5. **Wait for Deployment**
   - Takes 1-3 minutes
   - Status changes to **Succeeded**

6. **Note Deployment Name**
   - Copy the **Deployment name** (e.g., `gpt-4o-deployment`)
   - Save this for `.env` configuration

### Deploy via Azure CLI

```bash
# List available models
az cognitiveservices account list-models \
  --resource-group homebanking-rg \
  --name homebanking-foundry

# Create deployment
az cognitiveservices deployment create \
  --resource-group homebanking-rg \
  --name homebanking-foundry \
  --deployment-name gpt-4o-deployment \
  --model-name gpt-4o \
  --model-version "2024-08-01" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name Standard
```

---

## Step 3: Configure Authentication

The agent uses `DefaultAzureCredential` which tries multiple authentication methods in order.

### For Local Development (Recommended)

**Option 1: Azure CLI Login** (Easiest)

```powershell
# Login to Azure
az login

# Verify authentication
az account show

# Test that you can access your Foundry project
az cognitiveservices account show \
  --name homebanking-foundry \
  --resource-group homebanking-rg
```

**Option 2: Environment Variables**

```powershell
# Set Azure credential environment variables
$env:AZURE_TENANT_ID = "<your-tenant-id>"
$env:AZURE_CLIENT_ID = "<your-client-id>"
$env:AZURE_CLIENT_SECRET = "<your-client-secret>"
```

### For Production (Post-MVP)

Use **Managed Identity**:
1. Deploy agent to Azure (App Service, Container Apps, etc.)
2. Enable System-assigned managed identity
3. Grant identity **Cognitive Services User** role on Foundry resource

---

## Step 4: Assign Required Permissions

Your user account (or managed identity) needs access to the Foundry project.

### Via Azure Portal

1. **Navigate to Foundry Resource**
   - Go to Azure Portal → All Resources
   - Find your Foundry resource (e.g., `homebanking-foundry`)

2. **Open Access Control (IAM)**
   - Click **Access control (IAM)** in left menu
   - Click **+ Add** → **Add role assignment**

3. **Assign Role**
   - **Role**: Select **Cognitive Services User** or **Azure AI Developer**
   - **Assign access to**: User, group, or service principal
   - **Members**: Select your account or managed identity
   - Click **Review + assign**

### Via Azure CLI

```bash
# Get your user object ID
USER_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)

# Get Foundry resource ID
FOUNDRY_ID=$(az cognitiveservices account show \
  --name homebanking-foundry \
  --resource-group homebanking-rg \
  --query id -o tsv)

# Assign Cognitive Services User role
az role assignment create \
  --assignee $USER_OBJECT_ID \
  --role "Cognitive Services User" \
  --scope $FOUNDRY_ID
```

---

## Step 5: Configure Environment Variables

1. **Navigate to Agent Directory**
   ```powershell
   cd src/agent
   ```

2. **Copy Template to .env**
   ```powershell
   Copy-Item .env.template .env
   ```

3. **Edit .env File**
   ```powershell
   notepad .env
   ```

4. **Fill in Required Values**
   ```bash
   # Azure AI Foundry Project Configuration
   FOUNDRY_PROJECT_ENDPOINT=https://your-resource.ai.azure.com/api/projects/your-project
   FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-4o-deployment
   
   # HomeBanking API Configuration
   HOMEBANKING_API_BASE_URL=http://localhost:5091
   
   # Agent Server Configuration (defaults usually fine)
   AGENT_SERVER_PORT=8087
   AGENT_SERVER_HOST=127.0.0.1
   
   # Logging Configuration
   LOG_LEVEL=INFO
   ```

5. **Save and Close**

---

## Step 6: Verify Setup

1. **Ensure Virtual Environment is Activated**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Run Validation Script**
   ```powershell
   python validate_setup.py
   ```

   Expected output:
   ```
   ✅ PASS: Python Version
   ✅ PASS: Package Imports
   ✅ PASS: Module Structure
   🎉 Setup validation successful!
   ```

3. **Test Configuration Loading**
   ```powershell
   python -c "from config import AgentConfig; config = AgentConfig.from_env(); config.validate(); print('✓ Configuration valid')"
   ```

   If successful:
   ```
   ✓ Configuration valid
   ```

4. **Test Azure Authentication** (Optional)
   ```powershell
   python -c "from azure.identity import DefaultAzureCredential; cred = DefaultAzureCredential(); token = cred.get_token('https://cognitiveservices.azure.com/.default'); print('✓ Azure authentication successful')"
   ```

---

## Troubleshooting

### "FOUNDRY_PROJECT_ENDPOINT must be an HTTPS URL"

**Cause**: Endpoint is missing or formatted incorrectly

**Fix**: Ensure endpoint follows format:
```
https://<your-resource>.ai.azure.com/api/projects/<your-project>
```

### "DefaultAzureCredentialError: No credential available"

**Cause**: Not logged into Azure

**Fix**: Run `az login` and verify with `az account show`

### "Model deployment not found"

**Cause**: Model not deployed or wrong deployment name

**Fix**: 
1. Verify model is deployed in Foundry portal
2. Check deployment name matches exactly (case-sensitive)
3. Ensure deployment is in **Succeeded** state

### "Access Denied" or "403 Forbidden"

**Cause**: Insufficient permissions

**Fix**: 
1. Verify role assignment (Cognitive Services User or Azure AI Developer)
2. Wait 5-10 minutes for permission propagation
3. Try `az logout` then `az login` to refresh tokens

### "Region doesn't support model"

**Cause**: Selected model not available in chosen region

**Fix**: 
1. Check [model availability by region](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/model-region-support)
2. Either:
   - Choose a different model available in your region
   - Recreate Foundry project in a supported region

---

## Cost Considerations

### Foundry Resource Costs

- **Storage**: ~$0.05-0.20/GB/month (minimal for agent state)
- **Azure AI Search**: ~$250/month (Basic tier, auto-provisioned)
- **Key Vault**: ~$0.03/10K operations (minimal)

### Model Inference Costs (Pay-per-token)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Typical Transfer Request Cost |
|-------|----------------------|------------------------|-------------------------------|
| gpt-4o | $2.50 | $10.00 | ~$0.01-0.03 |
| gpt-4.1-mini | $0.40 | $1.60 | ~$0.002-0.005 |
| gpt-4.1 | $10.00 | $30.00 | ~$0.05-0.10 |

**For MVP testing**: Budget $10-50/month depending on usage volume.

### Cost Optimization Tips

1. Use `gpt-4.1-mini` for development/testing
2. Set token limits in agent configuration
3. Monitor usage in Azure portal (Cost Management)
4. Delete Foundry project when not actively developing

---

## Next Steps

After completing Foundry setup:

1. ✅ Verify `.env` is configured
2. ✅ Run `python validate_setup.py` successfully
3. ➡️ Proceed to **A003: Define agent instructions** in [plan-agent.md](../plan-agent.md)

---

## References

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Foundry Agent Service Overview](https://learn.microsoft.com/azure/ai-foundry/agents/overview)
- [Model & Region Availability](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/model-region-support)
- [Azure AI Pricing](https://azure.microsoft.com/pricing/details/cognitive-services/)
- [DefaultAzureCredential](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential)
