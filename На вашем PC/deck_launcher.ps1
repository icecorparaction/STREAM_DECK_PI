# !Предупреждаю!, если здесь у меня написано «User», то это не значит, что у вас на Raspberry Pi и у меня на компьютере то же самое. На Raspberry Pi у вас может быть другой никнейм самого аккаунта, и на ПК то же самое. Измените на свои.

param(
    [string]$PiHost = "user@192.168.0.127", # Здесь на Raspberry Pi
    [string]$PiLauncherCmd = "python3 /home/user/deck.py"# Здесь на Raspberry Pi
)

ssh $PiHost $PiLauncherCmd | ForEach-Object {
    $cmd = $_.Trim()
    Write-Host "Получена команда:" $cmd

    switch ($cmd) {
        "youtube"     { Start-Process "https://www.youtube.com" }
        "tlauncher"   { Start-Process "C:\Users\User\AppData\Roaming\.minecraft\TLauncher.exe" } # Здесь на ПК.
        "browser"     { Start-Process "https://www.google.com" }
        "capcut"     { Start-Process "C:\Users\User\AppData\Local\CapCut\Apps\CapCut.exe" }# Здесь на ПК.
        "settings"     { Start-Process ms-settings: }
        "filemanager" { Start-Process explorer } 
        "volume_up"   {     Start-Process -WindowStyle Hidden -FilePath "python.exe" -ArgumentList "C:\Users\User\vol_up.py"# Здесь на ПК.
                            Start-Sleep -Milliseconds 1
                            (New-Object -ComObject WScript.Shell).SendKeys([char]174) }
        "volume_down" { (New-Object -ComObject WScript.Shell).SendKeys([char]174) }

        "brightness_up" {
            Write-Host "🔆 Попытка увеличить яркость (реализация зависит от железа)"
            # Можем использовать WMI, например:
            $level = 80; (Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, $level)
        }

        "brightness_down" {
        Write-Host "🔅 Попытка уменьшить яркость"
        # Аналогично можно задать меньшее значение
        }
        "terminal"    { Start-Process cmd }
        "exit"        { 
            Write-Host "Выход из лаунчера." 
            break 
        }
        default       { Write-Warning "Неизвестная команда: $cmd" }
    }
}
