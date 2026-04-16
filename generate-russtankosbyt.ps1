function Generate-RusStankoProduct {
    param($artikul, $leadData)
    
    $templates = @{
        "1983*" = @{ name="Патрон 3-кулачковый"; type="задний/передний"; price="45 000-120 000"; group="Патроны" }
        "165*"  = @{ name="Кассета токарная"; type="правая/левая"; price="25 000-85 000"; group="Кассеты" }
        "163*"  = @{ name="Держатель резцов"; type="поворотный/фиксированный"; price="8 000-25 000"; group="Держатели" }
        "FU*"   = @{ name="Суппорт FU400R"; type="фрезерный"; price="20 000-45 000"; group="Суппорты" }
    }
    
    $template = $templates.Keys | Where-Object { $artikul -like $_ } | Select-Object -First 1
    if (-not $template) { $template = "Деталь токарной группы" }
    
    [PSCustomObject]@{
        Артикул = $artikul
        Название = "$($templates[$template].name) $($artikul)"
        Группа = $templates[$template].group
        Цена = "$($templates[$template].price) ₽"
        Наличие = @("В наличии", "Под заказ")[Get-Random]
        Срок = @("1-2 дня", "3-5 дней", "7-10 дней")[Get-Random]
        Описание = "Профессиональная оснастка для токарных станков $($artikul). Совместимость: 16К20, 1А62, 1М63, ТС1630. Высокая точность, ремонтопригодность, заводская гарантия 12 мес."
        SEO = "купить $($artikul) в Москве, патрон/держатель/суппорт для токарного станка, РУССтанкоСбыт"
        Вес = "$(10..150 | Get-Random) кг"
        Гарантия = "12 месяцев"
    }
}
