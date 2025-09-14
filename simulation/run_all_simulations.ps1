# simulation/run_all_simulations.ps1
$tests = @(
  @{ name='ci_simulated1_linters'; secret='dummy_LIN_123' },
  @{ name='ci_simulated2_nightly-build'; secret='dummy_NB_123' },
  @{ name='ci_simulated3_publish'; secret='dummy_PUB_123' },
  @{ name='ci_simulated4_langflow-nightly-build'; secret='dummy_LF_123' },
  @{ name='ci_simulated5_daily-checks-for-appcodeecommerce121'; secret='dummy_DC_123' },
  @{ name='ci_simulated6_diffreport'; secret='dummy_DR_123' },
  @{ name='ci_simulated7_ci'; secret='dummy_CI_123' }
)

foreach ($t in $tests) {
  $payload = @{ workflow = $t.name; secret = $t.secret } | ConvertTo-Json
  try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:5000/collect" -Method Post -Body $payload -ContentType "application/json"
    Write-Output "Sent $($t.name) -> response: $($resp | ConvertTo-Json)"
  } catch {
    Write-Output "Erreur en envoyant $($t.name): $_"
  }
  Start-Sleep -Milliseconds 300
}
