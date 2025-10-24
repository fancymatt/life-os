# AI Tool Development Guidelines

## 🚨 CRITICAL: Every Tool Needs a Config UI

**MANDATORY CHECKLIST** for every new AI tool you create:

### 1. Tool Implementation (`ai_tools/{tool_name}/`)
- [ ] `tool.py` - Core tool implementation
- [ ] `template.md` - Prompt template (REQUIRED for config UI)
- [ ] `README.md` - Documentation

### 2. Backend Integration
- [ ] Add to `configs/models.yaml` defaults section:
  ```yaml
  defaults:
    {tool_name}: "gemini/gemini-2.0-flash-exp"  # Or appropriate default model
  ```

### 3. Frontend Integration (REQUIRED!)
- [ ] Add route to `frontend/src/App.jsx`:
  ```javascript
  <Route path="{tool-name}" element={<ToolConfigPage />} />
  ```
- [ ] Add sidebar link to `frontend/src/components/layout/Sidebar.jsx`:
  ```javascript
  <NavLink to="/tools/{tool-name}" className="nav-link nav-link-sibling" onClick={onClose}>
    <span className="nav-icon">🔧</span>
    <span className="nav-label">{Tool Display Name}</span>
  </NavLink>
  ```

### 4. Custom Test Interface (if needed)
- [ ] For non-image tools, add custom test UI in `ToolConfigPage.jsx`:
  ```javascript
  {toolName === '{tool_name}' ? (
    /* Custom test interface */
    <div>
      {/* Tool-specific inputs */}
    </div>
  ) : (
    /* Default image upload interface */
  )}
  ```

### 5. API Endpoint (if tool needs standalone access)
- [ ] Add route to `api/routes/tool_configs.py` if tool needs custom test endpoint
- [ ] Update `run_tool_test_job()` function to handle new tool

## Example: Clothing Modifier Tool

✅ **Correct Implementation:**
1. Tool files created: `ai_tools/clothing_modifier/{tool.py,template.md,README.md}`
2. Added to `configs/models.yaml`: `clothing_modifier: "gemini/gemini-2.0-flash-exp"`
3. Route added: `<Route path="clothing-modifier" element={<ToolConfigPage />} />`
4. Sidebar link added: `<NavLink to="/tools/clothing-modifier">✂️ Clothing Modifier</NavLink>`
5. Custom test UI: Select clothing item + modification instruction (not image upload)
6. API endpoint: Uses existing `/clothing-items/{id}/modify` endpoint

## Why This Matters

**Users expect ALL tools to have:**
- 🎛️ **Model selection** - Choose which LLM to use
- 🌡️ **Temperature control** - Adjust creativity/determinism
- ✍️ **Prompt editing** - Customize the template
- 🧪 **Test interface** - Try the tool with different inputs
- 💾 **Save configuration** - Persist changes

**Without these, the tool is incomplete.**

## Common Mistakes to Avoid

❌ Creating tool without adding to `models.yaml`
❌ Creating tool without frontend route
❌ Creating tool without sidebar link
❌ Forgetting to rebuild API container after creating tool
❌ Using image upload UI for non-image tools
❌ Not testing the config UI before marking task complete

## Deployment Checklist

When you create a new tool:
1. ✅ Files created in `ai_tools/{tool_name}/`
2. ✅ Added to `configs/models.yaml`
3. ✅ Route added to `App.jsx`
4. ✅ Sidebar link added to `Sidebar.jsx`
5. ✅ Custom test UI added (if needed) to `ToolConfigPage.jsx`
6. ✅ **REBUILD API CONTAINER**: `docker-compose up -d --build api`
7. ✅ **REBUILD FRONTEND**: `docker-compose up -d --build frontend`
8. ✅ Test at `/tools/{tool-name}` - verify all features work

## File Locations Quick Reference

```
ai_tools/{tool_name}/tool.py           # Tool implementation
ai_tools/{tool_name}/template.md       # Prompt template (REQUIRED)
configs/models.yaml                     # Model defaults
frontend/src/App.jsx                    # Route definition (line ~175)
frontend/src/components/layout/Sidebar.jsx  # Sidebar link (line ~240-270)
frontend/src/pages/ToolConfigPage.jsx  # Custom test UI (line ~370-470)
```

---

**REMEMBER: If you create a tool without these steps, the user will have to ask you to add them later. Do it right the first time!**
