<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method = "html"  version="1.0" encoding="UTF-8" omit-xml-declaration="yes" standalone="yes" indent="no"  />

<xsl:param name="_page"></xsl:param>  <!-- NUM OF PAGE TO GENERATE (DON'T TOUCH) -->
<xsl:param name="_npp">8</xsl:param> <!-- NB OF PHOTOS PER PAGE -->


<xsl:template match="export">
    <!-- Calcul le nb de pages($nbpages) necessaire -->
    <xsl:variable name="nbpages"><xsl:value-of select="ceiling(count(//img) div $_npp) "/></xsl:variable>

    <xsl:if test="$_page &lt;= $nbpages">
    	<html>
    	<head>
    	<meta http-equiv="Content-Type" content="text/html" charset="UTF-8"></meta>
    	<title>album</title>
    	<style>
    	* {font-family: Verdana, helvetica, sans-serif; font-size: 8pt; color: #200;}

        div#liens {clear:both;padding:4px;}
        div#liens a {padding:4px;border:1px solid black;text-decoration:none;display:inline-block;margin:2px}
        div#liens a.sp1 {background:white}
        div#liens a.sp0 {background:#CCC}

        div.photo {background:#EEE;margin:4px;padding:4px;float:left;width:160px;height:190px;text-align:center;border:1px;border-style:outset;}
        div.photo img {border:1px;border-style:inset;}

    	</style>
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
        <xsl:for-each select="//img">
            <xsl:choose>
               <xsl:when test="($_npp * ($_page -1)) &lt; position() and position() &lt;= ($_npp * $_page)">
                    <xsl:apply-templates select="."/>
               </xsl:when>
               <xsl:otherwise>
               </xsl:otherwise>
            </xsl:choose>
        </xsl:for-each>

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
        <a href="{@src}">
            <img src="{@mini}" /> <br />
        </a>
        <xsl:value-of select="@hdate"/><br/>
        <xsl:value-of select="@comment"/><br/>
    </div>
</xsl:template>

</xsl:stylesheet>