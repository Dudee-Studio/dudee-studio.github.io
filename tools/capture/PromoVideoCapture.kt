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
