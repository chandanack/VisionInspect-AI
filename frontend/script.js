// ================= ELEMENTS =================

const imageInput = document.getElementById("imageInput");
const uploadArea = document.getElementById("uploadArea");
const previewContainer = document.getElementById("previewContainer");
const previewImage = document.getElementById("previewImage");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const analyzeBtn = document.getElementById("analyzeBtn");
const categorySelect = document.getElementById("categorySelect");
const resultContent = document.getElementById("resultContent");


// ================= DASHBOARD STATISTICS =================

const totalInspectionsElement =
    document.getElementById("totalInspections");

const goodProductsElement =
    document.getElementById("goodProducts");

const defectiveProductsElement =
    document.getElementById("defectiveProducts");


// ================= FILE SELECTION =================

imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) {
        return;
    }

    // Show image preview

    const reader = new FileReader();

    reader.onload = function (event) {

        previewImage.src = event.target.result;

    };

    reader.readAsDataURL(file);


    // Show file information

    fileName.textContent = file.name;

    fileSize.textContent =
        (file.size / 1024 / 1024).toFixed(2) + " MB";


    // Hide upload area

    uploadArea.classList.add("hidden");


    // Show preview

    previewContainer.classList.remove("hidden");

});


// ================= ANALYZE IMAGE =================

analyzeBtn.addEventListener("click", async function () {

    const file = imageInput.files[0];

    if (!file) {

        alert("Please select an image first.");

        return;
    }


    // Get selected category

    const category = categorySelect.value;


    // Create FormData

    const formData = new FormData();

    formData.append("category", category);

    formData.append("file", file);


    // Show loading state

    analyzeBtn.textContent = "⏳ Analyzing...";

    analyzeBtn.disabled = true;


    try {

        // Send image to FastAPI

        const response = await fetch(
            "http://127.0.0.1:8000/upload",
            {
                method: "POST",
                body: formData
            }
        );


        // Convert response to JSON

        const data = await response.json();

        console.log("AI Response:", data);


        // Check backend response

        if (!response.ok) {

            throw new Error(
                data.detail || "Backend request failed"
            );

        }


        // Show AI result

        showResult(data);


        // Refresh dashboard statistics

        loadInspectionStatistics();

    }

    catch (error) {

        console.error("Error:", error);

        resultContent.innerHTML = `

            <div class="result-icon">
                !
            </div>

            <h3>
                Connection Error
            </h3>

            <p>
                Could not connect to the AI backend.
                Make sure FastAPI is running.
            </p>

        `;

    }


    // Restore button

    analyzeBtn.textContent = "🔍 Analyze Image";

    analyzeBtn.disabled = false;

});


// ================= SHOW RESULT =================

function showResult(data) {


    // ==========================================
    // INVALID CATEGORY
    // ==========================================

    if (data.message === "Invalid category") {

        resultContent.innerHTML = `

            <div class="result-icon">
                !
            </div>

            <h3>
                Invalid Category
            </h3>

            <p>
                Please select a valid product category.
            </p>

        `;

        return;
    }


    // ==========================================
    // MISSING NORMAL FEATURES
    // ==========================================

    if (
        data.message ===
        "Normal features not found for this category"
    ) {

        resultContent.innerHTML = `

            <div class="result-icon">
                !
            </div>

            <h3>
                Model Data Not Found
            </h3>

            <p>
                Normal reference features are not available
                for ${data.category}.
            </p>

        `;

        return;
    }


    // ==========================================
    // GET INSPECTION REPORT
    // ==========================================

    const report = data.inspection_report;


    // Safety check

    if (!report) {

        resultContent.innerHTML = `

            <div class="result-icon">
                !
            </div>

            <h3>
                Invalid AI Response
            </h3>

            <p>
                The backend returned an unexpected response.
            </p>

        `;

        return;
    }


    // ==========================================
    // REPORT VALUES
    // ==========================================

    const inspectionId =
        report.inspection_id;

    const category =
        report.category;

    const prediction =
        report.prediction;

    const productStatus =
        report.product_status;

    const anomalyScore =
        Number(report.anomaly_score).toFixed(4);

    const threshold =
        Number(report.threshold).toFixed(4);

    const decision =
        report.decision;


    // ==========================================
    // IMAGE QUALITY
    // ==========================================

    const qualityStatus =
        report.quality_report.quality_status;

    const sharpness =
        report.quality_report.sharpness;

    const brightness =
        report.quality_report.brightness;

    const contrast =
        report.quality_report.contrast;

    const resolution =
        report.quality_report.resolution.width +
        " × " +
        report.quality_report.resolution.height;


    // ==========================================
    // GOOD PRODUCT
    // ==========================================

    if (prediction === "GOOD") {

        resultContent.innerHTML = `

            <div class="result-icon">
                ✓
            </div>

            <h3>
                GOOD PRODUCT
            </h3>

            <p>
                No significant anomaly detected.
            </p>

            <p>
                Inspection ID:
                <strong>${inspectionId}</strong>
            </p>

            <p>
                Category:
                <strong>${category}</strong>
            </p>

            <p>
                Anomaly Score:
                <strong>${anomalyScore}</strong>
            </p>

            <p>
                Threshold:
                <strong>${threshold}</strong>
            </p>

            <p>
                Decision:
                <strong>${decision}</strong>
            </p>

            <p>
                Product Status:
                <strong>${productStatus}</strong>
            </p>

            <h4>
                Image Quality
            </h4>

            <p>
                Status:
                <strong>${qualityStatus}</strong>
            </p>

            <p>
                Resolution:
                <strong>${resolution}</strong>
            </p>

            <p>
                Brightness:
                <strong>${brightness}</strong>
            </p>

            <p>
                Contrast:
                <strong>${contrast}</strong>
            </p>

            <p>
                Sharpness:
                <strong>${sharpness}</strong>
            </p>

        `;

    }


    // ==========================================
    // DEFECT / ANOMALY
    // ==========================================

    else {

        resultContent.innerHTML = `

            <div class="result-icon">
                !
            </div>

            <h3>
                ANOMALY DETECTED
            </h3>

            <p>
                The AI detected a significant visual
                difference from normal ${category} products.
            </p>

            <p>
                Inspection ID:
                <strong>${inspectionId}</strong>
            </p>

            <p>
                Category:
                <strong>${category}</strong>
            </p>

            <p>
                Anomaly Score:
                <strong>${anomalyScore}</strong>
            </p>

            <p>
                Threshold:
                <strong>${threshold}</strong>
            </p>

            <p>
                Decision:
                <strong>${decision}</strong>
            </p>

            <p>
                Product Status:
                <strong>${productStatus}</strong>
            </p>

            <h4>
                Image Quality
            </h4>

            <p>
                Status:
                <strong>${qualityStatus}</strong>
            </p>

            <p>
                Resolution:
                <strong>${resolution}</strong>
            </p>

            <p>
                Brightness:
                <strong>${brightness}</strong>
            </p>

            <p>
                Contrast:
                <strong>${contrast}</strong>
            </p>

            <p>
                Sharpness:
                <strong>${sharpness}</strong>
            </p>

        `;

    }

}


// ================= LOAD INSPECTION STATISTICS =================

async function loadInspectionStatistics() {

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/inspection-statistics"
        );


        const data = await response.json();

        console.log(
            "Inspection Statistics:",
            data
        );


        const statistics =
            data.statistics;


        // Update Total Inspections

        if (totalInspectionsElement) {

            totalInspectionsElement.textContent =
                statistics.total_inspections;

        }


        // Update Good Products

        if (goodProductsElement) {

            goodProductsElement.textContent =
                statistics.good_products;

        }


        // Update Defective Products

        if (defectiveProductsElement) {

            defectiveProductsElement.textContent =
                statistics.defective_products;

        }

    }

    catch (error) {

        console.error(
            "Could not load inspection statistics:",
            error
        );

    }

}


// ================= LOAD STATISTICS ON PAGE LOAD =================

loadInspectionStatistics();