// DtProbe: runs the original Joy of Convolution (Discrete Time) applet (reference/dt/
// DTConvolve.jar: Steve Crutchfield 1997, Swing update by Michael Ross 2001, JHU) under JDK 8
// and records ground truth for the browser port, like CtProbe does for the CT applet:
//   geometry.txt, <scenario>_<step>.png (1x captures), <scenario>.json (signal arrays).
//
// The DT applet uses the Java 1.1 listener model, so the probe sends real java.awt.event
// MouseEvents to the components (dispatchEvent on the event thread). That reaches the same
// listener code a student's click does, without OS mouse or DPI scaling involved. Panel fields
// are package-private in package DTConvolve, so they are read by reflection.
//
// Build/run (JDK 8 is not on PATH; see CLAUDE.md). The codebase must be reference/dt so the
// x_*.gif / h_*.gif button images load:
//   javac -cp reference/dt/classes -d tools/build tools/DtProbe.java
//   java  -cp "tools/build;reference/dt/classes" DtProbe reference/dt reference/captures/dt
import java.applet.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.lang.reflect.Field;
import java.net.URL;
import java.util.*;
import java.util.List;
import javax.imageio.ImageIO;
import javax.swing.*;

public class DtProbe {
    static JApplet applet;
    static File outDir;
    static final int W = 600, H = 600;   // <object width=600 height=600> on the JHU page
    static List<JLabel> xButtons = new ArrayList<JLabel>(), hButtons = new ArrayList<JLabel>();

    public static void main(String[] args) throws Exception {
        File ref = new File(args[0]).getAbsoluteFile();
        outDir = new File(args[1]);
        outDir.mkdirs();
        final URL base = new URL(ref.toURI().toURL(), "./");
        final AppletContext ctx = new AppletContext() {
            public AudioClip getAudioClip(URL u) { return null; }
            public Image getImage(URL u) { return Toolkit.getDefaultToolkit().getImage(u); }
            public Applet getApplet(String n) { return null; }
            public Enumeration<Applet> getApplets() { return Collections.enumeration(new ArrayList<Applet>()); }
            public void showDocument(URL u) {}
            public void showDocument(URL u, String t) {}
            public void showStatus(String s) {}
            public void setStream(String k, InputStream s) {}
            public InputStream getStream(String k) { return null; }
            public Iterator<String> getStreamKeys() { return new ArrayList<String>().iterator(); }
        };
        applet = (JApplet) Class.forName("DTConvolve.DTConvolve").newInstance();
        applet.setStub(new AppletStub() {
            public boolean isActive() { return true; }
            public URL getDocumentBase() { return base; }
            public URL getCodeBase() { return base; }
            public String getParameter(String n) { return null; }
            public AppletContext getAppletContext() { return ctx; }
            public void appletResize(int w, int h) {}
        });
        onEdt(new Runnable() { public void run() {
            JFrame f = new JFrame("DtProbe - Joy of Convolution DT (original, JHU)");
            f.getContentPane().setLayout(null);
            f.getContentPane().setPreferredSize(new Dimension(W, H));
            f.getContentPane().add(applet);
            applet.setBounds(0, 0, W, H);
            f.pack();
            applet.init();
            applet.validate();
            f.setVisible(true);
            applet.start();
        } });
        settle(2000);

        // Preset "buttons" are JLabels with an icon and a tooltip; x's five come first in the tree.
        List<JLabel> all = new ArrayList<JLabel>();
        collectLabels(applet.getContentPane(), all);
        for (JLabel l : all) (xButtons.size() < 5 ? xButtons : hButtons).add(l);

        PrintWriter g = new PrintWriter(new File(outDir, "geometry.txt"), "UTF-8");
        g.println("# Component bounds relative to the applet content pane (x, y, w, h). tools/DtProbe.java");
        dumpTree(g, applet.getContentPane(), 0, 0, 0);
        g.println();
        g.println("x preset labels (tree order): " + tips(xButtons));
        g.println("h preset labels (tree order): " + tips(hButtons));
        g.close();

        capture("d0_initial");
        hover(xButtons.get(0));
        capture("d0_hover_x_first_button");
        unhover(xButtons.get(0));

        scenario("d1_pulse_pulse", "Square pulse", "Square pulse", false);
        scenario("d2_pulse_exponential", "Square pulse", "Right-sided exponential", false);
        scenario("d3_squarewave_exponential", "One period of a square wave", "Right-sided exponential", false);
        scenario("d4_impulse_squarewave", "Unit Impulse", "One period of a square wave", false);
        scenario("d5_drawn_exponential", "Clear", "Right-sided exponential", true);

        System.out.println("done: " + outDir.getAbsolutePath());
        System.exit(0);
    }

    static void scenario(String name, String xTip, String hTip, boolean draw) throws Exception {
        press(find(xButtons, xTip), 5, 5);
        press(find(hButtons, hTip), 5, 5);
        if (draw) {
            // Freehand x: press then drag a rising line across the right half of the x panel.
            final JComponent p = (JComponent) field("xInputPanel");
            final int w = p.getWidth(), h = p.getHeight();
            mouse(p, MouseEvent.MOUSE_PRESSED, w / 2, h / 2);
            for (int i = 1; i <= 20; i++)
                mouse(p, MouseEvent.MOUSE_DRAGGED, w / 2 + i * (w / 2 - 4) / 20, h / 2 - i * (h / 4) / 20);
            mouse(p, MouseEvent.MOUSE_RELEASED, w - 4, h / 4);
            settle(200);
        }
        capture(name + "_a_signals");
        JComponent dual = (JComponent) field("xhDualPanel");
        int pw = dual.getWidth(), y = dual.getHeight() / 2;
        int[] stops = { pw / 4, pw / 2, 3 * pw / 4, pw - 2 };
        mouse(dual, MouseEvent.MOUSE_PRESSED, 1, y);
        int prev = 1;
        char tag = 'b';
        for (int stop : stops) {
            for (int x = prev + 1; x <= stop; x++) mouse(dual, MouseEvent.MOUSE_DRAGGED, x, y);
            settle(250);
            capture(name + "_" + (tag++) + "_px" + stop);
            prev = stop;
        }
        mouse(dual, MouseEvent.MOUSE_RELEASED, prev, y);
        writeJson(name);
    }

    static JLabel find(List<JLabel> ls, String tip) {
        for (JLabel l : ls) if (tip.equals(l.getToolTipText())) return l;
        throw new IllegalArgumentException("no preset label with tooltip " + tip + " in " + tips(ls));
    }

    static void press(JComponent c, int x, int y) throws Exception {
        mouse(c, MouseEvent.MOUSE_PRESSED, x, y);
        mouse(c, MouseEvent.MOUSE_RELEASED, x, y);
        mouse(c, MouseEvent.MOUSE_CLICKED, x, y);
        settle(200);
    }

    static void hover(JComponent c) throws Exception { mouse(c, MouseEvent.MOUSE_ENTERED, 5, 5); settle(200); }
    static void unhover(JComponent c) throws Exception { mouse(c, MouseEvent.MOUSE_EXITED, 5, 5); settle(200); }

    static void mouse(final Component c, final int id, final int x, final int y) throws Exception {
        onEdt(new Runnable() { public void run() {
            boolean down = id == MouseEvent.MOUSE_PRESSED || id == MouseEvent.MOUSE_DRAGGED;
            int button = (id == MouseEvent.MOUSE_DRAGGED || id == MouseEvent.MOUSE_ENTERED
                    || id == MouseEvent.MOUSE_EXITED) ? MouseEvent.NOBUTTON : MouseEvent.BUTTON1;
            c.dispatchEvent(new MouseEvent(c, id, System.currentTimeMillis(),
                    down ? InputEvent.BUTTON1_DOWN_MASK : 0, x, y, 1, false, button));
        } });
    }

    static Object field(String name) throws Exception {
        Field f = applet.getClass().getDeclaredField(name);
        f.setAccessible(true);
        return f.get(applet);
    }

    static Object call(Object o, String method) throws Exception {
        java.lang.reflect.Method m = o.getClass().getMethod(method);
        m.setAccessible(true);
        return m.invoke(o);
    }

    static String sigJson(Object panel, String getter) throws Exception {
        Object s = call(panel, getter);
        if (s == null) return "null";
        double[] d = (double[]) call(s, "getDataArrayCopy");
        StringBuilder sb = new StringBuilder("{\"xmin\": " + call(s, "getXMin") + ", \"xmax\": "
                + call(s, "getXMax") + ", \"maxIndex\": " + call(s, "getMaxIndex") + ", \"data\": [");
        for (int i = 0; i < d.length; i++) sb.append(i > 0 ? "," : "").append(d[i]);
        return sb.append("]}").toString();
    }

    static void writeJson(String name) throws Exception {
        Object dual = field("xhDualPanel");
        PrintWriter w = new PrintWriter(new File(outDir, name + ".json"), "UTF-8");
        w.println("{");
        w.println("  \"source\": \"original DT applet (Crutchfield 1997 / Ross 2001, JHU) run by tools/DtProbe.java\",");
        w.println("  \"n\": " + call(dual, "getN") + ",");
        w.println("  \"x\": " + sigJson(field("xInputPanel"), "getSignal") + ",");
        w.println("  \"h\": " + sigJson(field("hInputPanel"), "getSignal") + ",");
        w.println("  \"dual_signal1\": " + sigJson(dual, "getSignal1") + ",");
        w.println("  \"dual_signal2\": " + sigJson(dual, "getSignal2") + ",");
        w.println("  \"product\": " + sigJson(field("xhOutputPanel"), "getSignal") + ",");
        w.println("  \"y\": " + sigJson(field("yOutputPanel"), "getSignal"));
        w.println("}");
        w.close();
    }

    static void capture(final String name) throws Exception {
        final BufferedImage img = new BufferedImage(W, H, BufferedImage.TYPE_INT_RGB);
        onEdt(new Runnable() { public void run() {
            Graphics g = img.getGraphics();
            applet.printAll(g);
            g.dispose();
        } });
        ImageIO.write(img, "png", new File(outDir, name + ".png"));
    }

    static void collectLabels(Container c, List<JLabel> out) {
        for (Component k : c.getComponents()) {
            if (k instanceof JLabel && ((JLabel) k).getToolTipText() != null) out.add((JLabel) k);
            if (k instanceof Container) collectLabels((Container) k, out);
        }
    }

    static String tips(List<JLabel> ls) {
        StringBuilder sb = new StringBuilder();
        for (JLabel l : ls) sb.append(sb.length() > 0 ? " | " : "").append(l.getToolTipText());
        return sb.toString();
    }

    static void dumpTree(PrintWriter w, Component c, int ox, int oy, int depth) {
        Rectangle r = c.getBounds();
        int ax = depth == 0 ? 0 : ox + r.x, ay = depth == 0 ? 0 : oy + r.y;
        StringBuilder ind = new StringBuilder();
        for (int i = 0; i < depth; i++) ind.append("  ");
        String extra = "";
        if (c instanceof JLabel) {
            JLabel l = (JLabel) c;
            extra = " text=\"" + l.getText() + "\" tip=\"" + l.getToolTipText() + "\" icon="
                    + (l.getIcon() == null ? "none" : l.getIcon().getIconWidth() + "x" + l.getIcon().getIconHeight());
        }
        w.println(ind + c.getClass().getName() + extra + " abs=(" + ax + "," + ay + "," + r.width + "," + r.height + ")");
        if (c instanceof Container)
            for (Component k : ((Container) c).getComponents()) dumpTree(w, k, ax, ay, depth + 1);
    }

    static void onEdt(Runnable r) throws Exception {
        if (EventQueue.isDispatchThread()) r.run(); else EventQueue.invokeAndWait(r);
    }

    static void settle(int ms) throws Exception {
        Thread.sleep(ms);
        onEdt(new Runnable() { public void run() {} });
    }
}
