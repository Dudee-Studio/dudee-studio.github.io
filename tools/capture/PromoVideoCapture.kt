package io.github.captawesome89.einkaufsliste.ui

import android.graphics.Bitmap
import android.graphics.Canvas
import androidx.compose.ui.test.junit4.AndroidComposeTestRule
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextReplacement
import androidx.compose.ui.test.performTextInput
import androidx.compose.ui.test.hasScrollToNodeAction
import androidx.compose.ui.test.performScrollToNode
import androidx.compose.ui.test.hasSetTextAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.test.ext.junit.runners.AndroidJUnit4
import io.github.captawesome89.einkaufsliste.data.Purchase
import io.github.captawesome89.einkaufsliste.data.PurchaseItem
import io.github.captawesome89.einkaufsliste.data.ShopRepository
import io.github.captawesome89.einkaufsliste.data.parseEntries
import kotlinx.coroutines.runBlocking
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode
import java.io.File
import java.time.LocalDate

/**
 * Erzeugt die Screenshots für den Play Store (1080 × 1920) mit Beispieldaten.
 * Läuft nur mit SCREENSHOTS=true (Workflow „Store-Screenshots“); Ausgabe: app/build/screenshots/.
 */
@RunWith(AndroidJUnit4::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(qualifiers = "w360dp-h640dp-xxhdpi")
class PromoVideoCapture : UiTestBase() {

    /** Beispielartikel: Name → Abteilung und Preis. */
    private val catalog = mapOf(
        "Milch" to ("Milchprodukte" to 1.19), "Joghurt" to ("Milchprodukte" to 0.79), "Butter" to ("Milchprodukte" to 2.39),
        "Eier" to ("Milchprodukte" to 2.79), "Gouda" to ("Käse" to 2.29), "Parmesan" to ("Käse" to 3.49),
        "Brot" to ("Brot & Backwaren" to 2.49), "Äpfel" to ("Obst" to 2.99), "Bananen" to ("Obst" to 1.69),
        "Tomaten" to ("Gemüse" to 1.99), "Zwiebeln" to ("Gemüse" to 1.49), "Brokkoli" to ("Gemüse" to 1.99),
        "Spaghetti" to ("Nudeln & Reis" to 1.29), "Reis" to ("Nudeln & Reis" to 1.79),
        "Passierte Tomaten" to ("Konserven & Backzutaten" to 0.89), "Kaffee" to ("Kaffee & Tee" to 6.99),
        "Hackfleisch" to ("Fleisch & Fisch" to 4.99), "Hähnchenbrust" to ("Fleisch & Fisch" to 6.49),
        "Mineralwasser" to ("Getränke" to 0.49), "Toilettenpapier" to ("Drogerie" to 3.95),
    )
    private val prices = catalog.mapValues { it.value.second }

    private fun demoData() = runBlocking {
        val repo = ShopRepository(db)
        catalog.forEach { (name, v) -> repo.createProduct(name, v.first, v.second, 0) }
        val byName = dao.allProducts().associateBy { it.name }
        listOf("Milch", "Brot", "Eier", "Kaffee", "Äpfel").forEach { dao.setFavorite(byName.getValue(it).id, true) }
        listOf("Milch" to 2, "Eier" to 1, "Butter" to 1, "Kaffee" to 1, "Reis" to 2).forEach { (name, stock) ->
            dao.setStock(byName.getValue(name).id, stock)
        }
        repo.saveDish(null, "Spaghetti Bolognese", "Hauptgerichte", null, listOf("Spaghetti" to 1, "Hackfleisch" to 1, "Passierte Tomaten" to 2, "Zwiebeln" to 1, "Parmesan" to 1))
        repo.saveDish(null, "Hähnchen mit Reis", "Hauptgerichte", null, listOf("Hähnchenbrust" to 1, "Reis" to 1, "Brokkoli" to 2))
        repo.saveDish(null, "Frühstück", "Frühstück", null, listOf("Brot" to 1, "Butter" to 1, "Eier" to 1, "Kaffee" to 1))

        // Ein halbes Jahr Einkäufe für die Analyse
        val today = LocalDate.now()
        val baskets = listOf(
            listOf("Milch" to 2, "Brot" to 1, "Äpfel" to 1, "Kaffee" to 1, "Joghurt" to 4),
            listOf("Hackfleisch" to 1, "Spaghetti" to 2, "Passierte Tomaten" to 2, "Zwiebeln" to 1, "Parmesan" to 1),
            listOf("Hähnchenbrust" to 1, "Reis" to 1, "Brokkoli" to 2, "Mineralwasser" to 12, "Toilettenpapier" to 1),
            listOf("Milch" to 3, "Butter" to 1, "Eier" to 2, "Bananen" to 1, "Gouda" to 1),
        )
        var at = 1L
        for (week in 0 until 26) {
            val basket = baskets[week % baskets.size]
            val date = today.minusWeeks(week.toLong()).minusDays(1)
            val items = basket.map { (n, q) -> PurchaseItem(purchaseId = 0, productId = byName[n]?.id, name = n, qty = q, price = prices[n]) }
            val total = items.sumOf { (it.price ?: 0.0) * it.qty } * (1.0 + (week % 5) * 0.12)
            val id = dao.insertPurchase(Purchase(date = date.toString(), at = at++, total = Math.round(total * 100) / 100.0, count = items.size))
            dao.insertPurchaseItems(items.map { it.copy(purchaseId = id) })
        }

        repo.addToList(parseEntries("2x Milch, Brot, 6 Äpfel, Bananen, Tomaten, Gouda, Spaghetti, 2 Passierte Tomaten, Kaffee"))
        dao.listRows().filter { it.name in setOf("Brot", "Milch") }.forEach { repo.setDone(it.entryId, true) }
    }

    /** Das Fenster direkt in ein Bitmap zeichnen – captureToImage wartet unter Robolectric vergeblich auf ein neues Bild. */
    private fun capture(name: String, modal: Boolean = false, folder: String = "build/screenshots") {
        compose.waitForIdle()
        val dialog = org.robolectric.shadows.ShadowDialog.getLatestDialog()
        val view = if (modal && dialog?.isShowing == true) dialog.window!!.decorView.rootView
            else (compose as AndroidComposeTestRule<*, *>).activity.window.decorView.rootView
        val bitmap = Bitmap.createBitmap(view.width, view.height, Bitmap.Config.ARGB_8888)
        view.draw(Canvas(bitmap))
        val dir = File(folder).apply { mkdirs() }
        File(dir, "$name.png").outputStream().use { bitmap.compress(Bitmap.CompressFormat.PNG, 100, it) }
    }

    @Test
    fun captureStore42() {
        assumeTrue(System.getProperty("screenshots") == "true")
        demoData()
        val repo = ShopRepository(db)
        vm.setPro(false)
        runBlocking {
            dao.deleteDone()
            dao.allProducts().forEach { repo.setListQty(it.id, 0) }
            val banana = dao.allProducts().single { it.name == "Bananen" }
            db.openHelper.writableDatabase.execSQL("DELETE FROM purchase_items WHERE productId = ?", arrayOf(banana.id))
            for (week in 1..3) {
                val id = dao.insertPurchase(Purchase(date = LocalDate.now().minusWeeks(week.toLong()).toString(), at = 100L + week, total = 2.97, count = 1))
                dao.insertPurchaseItems(listOf(PurchaseItem(purchaseId = id, productId = banana.id, name = banana.name, qty = 3, price = 0.99, wasOffer = true)))
            }
            val milk = dao.allProducts().single { it.name == "Milch" }
            repo.saveRecurringNeed(io.github.captawesome89.einkaufsliste.data.RecurringNeed(milk.id, 2, 7, LocalDate.now().plusDays(7).toString()))
        }
        waitFor { vm.suggestions.value.any { it.name == "Bananen" } }
        tab("Artikel").performClick()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("Bananen"))
        capture("01-catalog", folder = "build/store42")
        tab("Liste").performClick()
        capture("01b-list-forecast", folder = "build/store42")
        textNode("Ansehen").performClick()
        capture("02-forecast", modal = true, folder = "build/store42")
        val count = vm.suggestions.value.size
        textNode("$count auf die Liste").performClick()
        waitFor { openQty("Bananen") == 3 }
        tab("Artikel").performClick()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("Bananen"))
        capture("03-catalog-filled", folder = "build/store42")
        tab("Liste").performClick()
        capture("03b-list-filled", folder = "build/store42")
        compose.onNodeWithContentDescription("Mehr").performClick()
        textNode("Einkaufsvorschlag").performClick()
        textNode("Regelmäßigen Bedarf hinzufügen").performClick()
        waitForText("2× Milch")
        capture("04-recurring", modal = true, folder = "build/store42")
        textNode("Fertig").performClick()
        textNode("Abbrechen").performClick()
        tab("Gerichte").performClick()
        capture("05-dishes", folder = "build/store42")
        textNode("Spaghetti Bolognese").performClick()
        capture("06-ingredients", modal = true, folder = "build/store42")
        textNode("5 auf die Liste").performClick()
        tab("Liste").performClick()
        capture("07-prepared", folder = "build/store42")
        val rows = runBlocking { dao.listRows().filterNot { it.done } }
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText(rows.first().name))
        textNode(rows.first().name).performClick()
        waitFor { vm.list.value.any { it.done } }
        waitForText("Später")
        textNode("Später").performClick()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("IM WAGEN", substring = true))
        compose.onNode(hasText("IM WAGEN", substring = true)).performClick()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText(rows.first().name))
        capture("08-check-one", folder = "build/store42")
        for (index in 1..3) {
            compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText(rows[index].name))
            runBlocking { repo.setDone(rows[index].entryId, true) }
            waitFor { vm.list.value.count { it.done } >= index + 1 }
            compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText(rows[index].name))
            capture(listOf("09-check-two", "10-check-three", "10b-check-four")[index - 1], folder = "build/store42")
        }
        vm.setPro(true)
        capture("11-group-before", folder = "build/store42")
        runBlocking { repo.addToList(parseEntries("Zitronen")) }
        waitFor { openQty("Zitronen") == 1 }
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("Zitronen"))
        capture("12-group-added", folder = "build/store42")
        fakeLookup.products["4006381333931"] = io.github.captawesome89.einkaufsliste.lookup.ProductInfo("4006381333931", "Haferdrink", category = "Getränke")
        fakeScanner.queue += "4006381333931"
        compose.onNodeWithContentDescription("Barcode scannen").performClick()
        waitFor { openQty("Haferdrink") == 1 }
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("Haferdrink"))
        capture("13-scanned", folder = "build/store42")
        runBlocking { dao.listRows().filterNot { it.done }.forEach { repo.setDone(it.entryId, true) } }
        waitFor { vm.list.value.all { it.done } }
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("Einkauf abschließen"))
        capture("13b-ready", folder = "build/store42")
        textNode("Einkauf abschließen").performClick()
        capture("14-checkout", modal = true, folder = "build/store42")
        textNode("Einkauf speichern").performClick()
        waitForText("Die Liste ist leer")
        capture("15-finished", folder = "build/store42")
        tab("Analyse").performClick()
        textNode("Weitere Auswertungen anzeigen").performScrollTo().performClick()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("AUSGABEN PRO MONAT"))
        capture("16-analysis", folder = "build/store42")
    }

    @Test
    fun captureForecast() {
        assumeTrue(System.getProperty("screenshots") == "true")
        vm.setPro(false)
        runBlocking {
            val repo = ShopRepository(db)
            for (name in listOf("Kaffee", "Eier", "Bananen")) repo.createProduct(name, "Lebensmittel", 1.99, 0)
            val products = dao.allProducts().associateBy { it.name }
            dao.setStock(products.getValue("Eier").id, 1)
            for (weeks in 1..4) {
                val id = dao.insertPurchase(Purchase(date = LocalDate.now().minusWeeks(weeks.toLong()).toString(), at = weeks.toLong(), total = 11.94, count = 3))
                dao.insertPurchaseItems(products.values.map { PurchaseItem(purchaseId = id, productId = it.id, name = it.name, qty = 2, price = 1.99) })
            }
        }
        waitFor { vm.suggestions.value.size == 3 }
        compose.onNodeWithContentDescription("Mehr").performClick()
        textNode("Einkaufsvorschlag").performClick()
        waitForText("3 auf die Liste")
        capture("forecast", modal = true, folder = "build/promo")
    }

    @Test
    fun capturePromo() {
        assumeTrue(System.getProperty("screenshots") == "true")
        demoData()
        vm.setStoreName("Supermarkt")
        vm.setPro(true)
        waitForText("Supermarkt · 7 offen")
        tab("Artikel").performClick()
        waitForText(" Artikel · ", substring = true)
        capture("catalog-before", folder = "build/promo")
        compose.onNodeWithContentDescription("Brokkoli auf die Liste").performClick()
        waitFor { openQty("Brokkoli") == 1 }
        waitForDescription("Brokkoli mehr")
        capture("catalog-after", folder = "build/promo")
        compose.onNode(hasSetTextAction()).performTextInput("Milch")
        waitForText("Milch")
        textNode("Milch").performClick()
        expand("Foto & Barcode")
        textNode("Scannen").performScrollTo()
        capture("barcode-before", true, "build/promo")
        fakeScanner.queue += "4000417025005"
        textNode("Scannen").performClick()
        waitForText("Barcode 4000417025005")
        textNode("Neu scannen").performScrollTo()
        capture("barcode-after", true, "build/promo")
        textNode("Fertig").performClick()
        tab("Gerichte").performClick()
        waitForText("Zutaten auf die Liste", substring = true)
        capture("dishes", folder = "build/promo")
        textNode("Spaghetti Bolognese").performClick()
        waitForText("5 auf die Liste")
        capture("dish-ingredients", true, "build/promo")
        textNode("5 auf die Liste").performClick()
        tab("Liste").performClick()
        capture("list-before", folder = "build/promo")
        fakeLookup.products["4006381333931"] = io.github.captawesome89.einkaufsliste.lookup.ProductInfo("4006381333931", "Haferdrink", category = "Getränke")
        fakeScanner.queue += "4006381333931"
        compose.onNodeWithContentDescription("Barcode scannen").performClick()
        waitFor { openQty("Haferdrink") == 1 }
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("Haferdrink"))
        waitForText("Haferdrink")
        capture("spontaneous", folder = "build/promo")
        tab("Mehr").performClick()
        textNode("Gemeinsam einkaufen").performClick()
        waitForText("Einladung annehmen")
        capture("family", true, "build/promo")
        compose.onNodeWithContentDescription("Schließen").performClick()
        tab("Analyse").performClick()
        waitForText("Diesen Monat")
        textNode("Weitere Auswertungen anzeigen").performScrollTo().performClick()
        compose.onNode(hasScrollToNodeAction()).performScrollToNode(hasText("AUSGABEN PRO MONAT"))
        waitForText("AUSGABEN PRO MONAT")
        capture("analysis-pro", folder = "build/promo")
    }
}
