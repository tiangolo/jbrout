<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method = "html"  version="1.0" encoding="ISO-8859-1" omit-xml-declaration="yes" standalone="yes" indent="no"  />

<xsl:param name="_page"></xsl:param>  <!-- NUM OF PAGE TO GENERATE (DON'T TOUCH)-->
<xsl:param name="_npp">10</xsl:param> <!-- NB OF PHOTOS PER PAGE -->


<xsl:template match="export">
    <!-- Calcul le nb de pages($nbpages) necessaire -->
    <xsl:variable name="nbpages"><xsl:value-of select="ceiling(count(//img) div $_npp)"/></xsl:variable>

    <xsl:if test="$_page &lt;= $nbpages">
    	<html>
    	<head>
    	<meta http-equiv="Content-Type" content="text/html" charset="iso-8859-1"></meta>
    	<title>album</title>
    	<style>
    	* {font-family: Verdana, helvetica, sans-serif; font-size: 8pt; color: #fff;}
        body {background:black;}

        div#liens {clear:both;padding:1px;}
        div#liens a {color:black;padding:4px;border:1px solid black;text-decoration:none;display:inline-block;margin:2px}
        div#liens a.sp1 {background:white}
        div#liens a.sp0 {background:#CCC}

        div#photos {position:absolute;left:0px;top:30px; height:600px;overflow:scroll;width:160px;}
        div.photo {margin:4px;width:140px;text-align:center}
        div.photo img {border:1px;border-style:inset;}

        div#visu { position:absolute;left:180px;top:30px;}

    	</style>
    	<script>
    	function change(i)
    	{
    	   document.getElementById('image').src=i;
    	   document.getElementById('link').href=i;
    	}
    	</script>
    	</head>
    	<body leftmargin="0" topmargin="0">

        <!-- Construit la barre des liens vers les differentes pages -->
        <div id="liens">Page
            <xsl:call-template name="pagesLiens">
                <xsl:with-param name="i" select="1"/>
                <xsl:with-param name="np" select="$nbpages"/>
            </xsl:call-template>
        </div>

        <!-- et enfin affiche les images de la page -->
        <div id="photos">
        <xsl:for-each select="//img">
            <xsl:choose>
               <xsl:when test="($_npp * ($_page -1)) &lt; position() and position() &lt;= ($_npp * $_page)">
                    <xsl:apply-templates select="."/>
               </xsl:when>
               <xsl:otherwise>
               </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>
        </div>

        <div id="visu">
            <a id="link">
                <xsl:attribute name="href"><xsl:value-of select="//img[position() = 1+($_npp * ($_page - 1))]/@src"/></xsl:attribute>
                <img id="image" width="700px">
                      <xsl:attribute name="src"><xsl:value-of select="//img[position() = 1+($_npp * ($_page - 1))]/@src"/></xsl:attribute>
                </img>
            </a>
        </div>


    	</body>
    	</html>
    </xsl:if>
</xsl:template>


<!-- ====================================================================== -->
<xsl:template name="pagesLiens">
<!-- ====================================================================== -->
<xsl:param name="i"/>
<xsl:param name="np"/>
    <a>
      <xsl:attribute name="href">page<xsl:value-of select="$i"/>.html</xsl:attribute>
        <xsl:choose>
           <xsl:when test="$i = $_page">
                <xsl:attribute name="class">sp1</xsl:attribute>
                <xsl:value-of select="$i"/>
           </xsl:when>
           <xsl:otherwise>
                <xsl:attribute name="class">sp0</xsl:attribute>
                <xsl:value-of select="$i"/>
           </xsl:otherwise>
        </xsl:choose>
    </a>

    <xsl:if test="$i &lt; $np">
      <xsl:call-template name="pagesLiens">
        <xsl:with-param name="i" select="$i + 1"/>
        <xsl:with-param name="np" select="$np"/>
      </xsl:call-template>
    </xsl:if>
</xsl:template>


<!-- ====================================================================== -->
<xsl:template match="img">
<!-- ====================================================================== -->
    <div class="photo">
        <a href="#">
            <xsl:attribute name="onClick">change('<xsl:value-of select="@src"/>');return 0;</xsl:attribute>
            <img src="{@mini}" /> <br />
        </a>
    </div>
</xsl:template>

</xsl:stylesheet>