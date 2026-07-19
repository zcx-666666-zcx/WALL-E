export async function bootstrapApp(loadConfig, mountApp) {
  try {
    await loadConfig()
  } catch {
    // The app can still show an explicit offline state when config loading fails.
  }
  return mountApp()
}

