# Final Project (part 1)

This is the final project for my Terrain Analysis and Hydrologic Modelling course held in Autumn semester of 2024. The main goal for this was to create an (imagenary) landscape evolution model. The DEM used in the project has a spatial resolution about 5 meters and extent of (35.75 139.255, 35.80 139.30) (in EPSG: 6668, *JGD 2011*). A normal fault is assigned to the model along the (model) coordinate of (200 750), (400 620), (650 350) & (720 100). The model total duration was 100 thousand years and the interval was a thousand year.

## Result

**Fig. 1.** 2D representation of the model.

![2D simulation GIF](result\2D-Simulation.gif)

**Fig. 2.** 3D representation of the model.

![3D simulation GIF](result\3D-Simulation.gif)

**Fig. 3.** The water body of the model.

![Drainage simulation GIF](result\2D-Drainage-Simulation.gif)

## References & Softwares

1. [基盤地図情報ダウンロードサービス](https://fgd.gsi.go.jp/download/menu.php) (*Base Map Information Download Service*) from Geospatial Information Authority of Japan - The DEM source. <sup>[note 1]</sup>
2. [基盤地図情報 標高DEMデータ変換ツール](https://www.ecoris.co.jp/contents/demtool.html) (*Base Map Information DEM Cata Conversion Tool*) from Ecoris Inc. - Used to convert file format from JPGIS to GeoTIFF.
3. QGIS - Used to access GDAL's fill nodata commend.
4. ArcGIS Pro - Used to perform fill in the modified DEM.
5. [Landlab](https://landlab.github.io/) - Used to perform landscape eveolution model.

### Note

1. According to the [Terms of Services](https://fgd.gsi.go.jp/download/terms.html) of GSI, the citation is required; without GSI's permission, the distribution of modified DEM is prohibitted. The following is the Japanese citation. 数値標高モデル－5mメッシュ－5A（国土地理院）を加工して作成。