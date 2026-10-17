package io.github.captawesome89.einkaufsliste.catalog

import android.app.Application
import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import androidx.compose.runtime.*
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.ViewModelStore
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import io.github.captawesome89.einkaufsliste.ShopViewModel
import io.github.captawesome89.einkaufsliste.data.*
import io.github.captawesome89.einkaufsliste.ui.*
import io.github.captawesome89.einkaufsliste.ui.theme.EinkaufslisteTheme
import kotlinx.coroutines.runBlocking
import org.junit.*
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode
import java.io.File

/** Real current Compose UI; only remote responses and test photos are prepared demo data. */
@RunWith(AndroidJUnit4::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(qualifiers = "w360dp-h720dp-xxhdpi")
class CatalogFeatureCapture {
    @get:Rule val compose = createComposeRule()
    private lateinit var db: AppDatabase
    private lateinit var vm: ShopViewModel
    private lateinit var app: Application
    private val store = ViewModelStore()
    private var phase by mutableStateOf("new")
    private var ownId = 0L
    @Volatile private var photoCount = 0
    private val folder = File("build/catalog-feature-captures")
    private val photo = File("../../dudee-studio.github.io/assets/einkaufsliste/catalog-v1.1/apples.png")
    private val own = mutableListOf<Pair<Int,String>>()
    @Before fun before() {
        app = ApplicationProvider.getApplicationContext()
        app.getSharedPreferences("einkaufsliste", Context.MODE_PRIVATE).edit().clear()
            .putBoolean("seeded", true).putBoolean("proTest", true).apply()
        db = Room.inMemoryDatabaseBuilder(app, AppDatabase::class.java).build()
        val repo = ShopRepository(db)
        runBlocking { repo.addCategory("Obst"); repo.addCategory("Picknick") }
        val backend = object : CatalogBackend {
            override suspend fun search(text: String) = listOf(CommunityArticle("demo_0", "Äpfel", "Obst", QtyUnit.KG.name, 2.49, "Wochenmarkt", "2026-10-17", true, "demo"))
            override suspend fun own() = own.toList()
            override suspend fun publish(slot: Int, item: CommunityArticle, photo: String?) { own.add(slot to item.name) }
            override suspend fun withdraw(slot: Int) { own.removeAll { it.first == slot } }
            override suspend fun deleteAll() { own.clear() }
            override suspend fun photo(item: CommunityArticle): String? = PhotoStore.saveDownloaded(app, photo.readBytes(), "community_").also { photoCount++ }
            override suspend fun report(item: CommunityArticle) { }
        }
        vm = ViewModelProvider(store, viewModelFactory { initializer {
            ShopViewModel(app, repo, syncBackendFactory = { null }, onlineServicesFactory = { null }, catalogFactory = { backend })
        } })[ShopViewModel::class.java]
        vm.acceptCatalog(false)
    }
    @After fun after() { store.clear(); db.close() }
    private fun capture(name: String) {
        compose.waitForIdle()
        val dialog = org.robolectric.shadows.ShadowDialog.getLatestDialog()
        val view = if (dialog?.isShowing == true) dialog.window!!.decorView.rootView
            else (compose as androidx.compose.ui.test.junit4.AndroidComposeTestRule<*, *>).activity.window.decorView.rootView
        val bmp = Bitmap.createBitmap(view.width, view.height, Bitmap.Config.ARGB_8888)
        view.draw(Canvas(bmp)); folder.mkdirs()
        File(folder,"$name.png").outputStream().use { bmp.compress(Bitmap.CompressFormat.PNG,100,it) }
        println("Captured $name")
    }
    private fun waitFor(condition: () -> Boolean) {
        val deadline = System.currentTimeMillis() + 10000
        while (true) {
            compose.mainClock.advanceTimeBy(50)
            compose.waitForIdle()
            if (condition()) return
            check(System.currentTimeMillis() < deadline) { "Capture state did not settle" }
            Thread.sleep(20)
        }
    }
    @Test fun captureFeature() {
        compose.setContent { EinkaufslisteTheme {
            when(phase) {
                "new" -> NewProductDialog(vm, "") { phase = "saved" }
                "own" -> ProductDialog(vm, ownId) { phase = "saved" }
                else -> CatalogScreen(vm, onOpenProduct = {})
            }
        } }
        compose.waitForIdle(); capture("01-empty")
        val input = compose.onNode(hasSetTextAction() and hasText("Name"))
        input.performTextReplacement("Ap"); capture("02-typing")
        input.performTextReplacement("Apfel")
        compose.onNodeWithText("Im gemeinsamen Katalog suchen · Pro").performClick()
        waitFor { compose.onAllNodesWithText("Übernehmen").fetchSemanticsNodes().isNotEmpty() }
        capture("03-results")
        compose.onNodeWithText("Übernehmen").performClick()
        waitFor { photoCount > 0 }
        repeat(5) { Thread.sleep(50); compose.waitForIdle() }
        capture("04-copy")
        compose.onNodeWithText("Weitere Angaben", substring = true).performScrollTo().performClick()
        compose.onNodeWithText("Obst", useUnmergedTree = true).performScrollTo().performClick()
        compose.onNodeWithText("Picknick", useUnmergedTree = true).performClick()
        capture("05-category")
        compose.onNodeWithText("Anlegen", useUnmergedTree = true).performClick()
        waitFor { phase == "saved" && vm.products.value.any { it.name == "Äpfel" } }
        capture("05b-saved")
        // Own article, not redistribution of an imported community photo.
        runBlocking {
            val repo = ShopRepository(db)
            repo.createProduct("Äpfel vom Wochenmarkt", "Obst", 2.49, 0, QtyUnit.KG, "Wochenmarkt")
            ownId = repo.dao.productByName("Äpfel vom Wochenmarkt")!!.id
            repo.setProductImage(ownId, PhotoStore.saveDownloaded(app, photo.readBytes(), "camera_demo_"))
        }
        waitFor { vm.products.value.size == 2 }
        compose.runOnIdle { phase = "own" }
        compose.onNodeWithText("Artikel öffentlich bereitstellen").performScrollTo().performClick()
        compose.waitForIdle(); capture("06-share-private")
        compose.onAllNodes(isToggleable())[2].performSemanticsAction(androidx.compose.ui.semantics.SemanticsActions.OnClick) { it() }
        compose.mainClock.advanceTimeBy(500)
        capture("07-share-options")
        compose.onNodeWithText("Jetzt veröffentlichen").performSemanticsAction(androidx.compose.ui.semantics.SemanticsActions.OnClick) { it() }
        waitFor { own.size == 1 }
        compose.onNodeWithText("Artikel veröffentlicht.").performScrollTo()
        capture("08-published")
    }
}
