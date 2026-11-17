// CtProbe: runs Steve Crutchfield's original Joy of Convolution applet (reference/ct/*.class,
// JHU, 1996) under JDK 8 and records ground truth for the browser port:
//   - geometry.txt : every AWT component's bounds inside the 480x600 applet (the GridBag result,
//                    which cannot be read from the source alone)
//   - <scenario>_<step>.png : 1x pixel captures of the applet after scripted user actions
//   - <scenario>.json : the internal signal arrays (x, h, integrand, y, y-shown) after the sweep
//
// It lives in the default package on purpose: the applet's classes are package-private
// default-package classes, so the probe can call their mouseDown()/mouseDrag() handlers
// directly. That is deterministic (no OS mouse, no DPI scaling) and drives exactly the code
// a real click would reach.
//
// Build/run (JDK 8 is not on PATH; see CLAUDE.md):
//   javac -cp reference/ct -d tools/build tools/CtProbe.java
//   java  -cp "tools/build;reference/ct" CtProbe reference/ct reference/captures/ct
import java.applet.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.net.URL;
import java.util.*;
import javax.imageio.ImageIO;

public class CtProbe {
    static Convolve applet;
    static File outDir;
    static ControllableSignal cx, ch;
    static ConvPanel conv;
    static SigPanel integ;
    static ConvSigPanel ypanel;

    public static void main(String[] args) throws Exception {
        File ref = new File(args[0]).getAbsoluteFile();
        outDir = new File(args[1]);
        outDir.mkdirs();
        final URL base = ref.toURI().toURL();
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
        applet = new Convolve();
        applet.setStub(new AppletStub() {
            public boolean isActive() { return true; }
            public URL getDocumentBase() { return base; }
            public URL getCodeBase() { return base; }
            public String getParameter(String n) { return null; }
            public AppletContext getAppletContext() { return ctx; }
            public void appletResize(int w, int h) {}
        });

        final Frame f = new Frame("CtProbe - Joy of Convolution (original, JHU)");
        f.setLayout(null);
        f.addNotify();
        Insets in = f.getInsets();
        f.setSize(480 + in.left + in.right, 600 + in.top + in.bottom);
        f.add(applet);
        applet.setBounds(in.left, in.top, 480, 600);   // the <applet width=480 height=600> tag
        applet.init();
        applet.validate();
        f.setVisible(true);
        applet.start();
        settle(1500);   // panels create their signals on first paint()

        Component[] kids = applet.getComponents();   // add order in Convolve.init()
        cx = (ControllableSignal) kids[0];
        ch = (ControllableSignal) kids[1];
        conv = (ConvPanel) kids[2];
        integ = (SigPanel) kids[3];
        ypanel = (ConvSigPanel) kids[4];

        PrintWriter g = new PrintWriter(new File(outDir, "geometry.txt"), "UTF-8");
        g.println("# Component bounds relative to the applet (x, y, w, h). Captured by tools/CtProbe.java");
        dumpTree(g, applet, 0, 0, 0);
        g.println();
        g.println("ConvPanel fSigLength=" + conv.fSigLength + " fAmplitude=" + conv.fAmplitude
                + " fScale=" + conv.fScale);
        g.println("x signal length=" + sig(cx).getLength() + " amplitude=" + sig(cx).fAmplitude);
        g.println("h signal length=" + sig(ch).getLength() + " amplitude=" + sig(ch).fAmplitude);
        g.println("integrand panel signal length=" + integ.getSignal().getLength()
                + " amplitude=" + integ.getSignal().fAmplitude);
        g.println("y panel signal length=" + ypanel.getSignal().getLength()
                + " amplitude=" + ypanel.getSignal().fAmplitude);
        g.close();

        capture("s0_initial");

        int W = conv.fSigLength;
        int[] stops = { W / 4, W / 2, 3 * W / 4, W - 1 };
        scenario("s1_pulse_pulse", "pulse", "pulse", null, stops);
        scenario("s2_pulse_decay", "pulse", "decay", null, stops);
        scenario("s3_doublepulse_decay", "double pulse", "decay", null, stops);
        scenario("s4_decay_doublepulse", "decay", "double pulse", null, stops);
        scenario("s5_drawn_pulse", "clear", "pulse", "ramp", stops);

        // A click with no drag, after a fresh preset: shows the single revealed y point.
        press(cx, "pulse"); press(ch, "decay");
        onEdt(new Runnable() { public void run() { conv.mouseDown(null, W / 2, 0); } });
        settle(300);
        capture("s6_single_click");

        System.out.println("done: " + outDir.getAbsolutePath());
        f.dispose();
        System.exit(0);
    }

    static Signal sig(ControllableSignal c) { return c.getSigPanel().getSignal(); }

    static void scenario(String name, String xPreset, String hPreset, String draw, int[] stops)
            throws Exception {
        press(cx, xPreset);
        press(ch, hPreset);
        if ("ramp".equals(draw)) {
            // Freehand x: one press then a drag, like a student sketching a rising ramp.
            final MouseSigPanel p = cx.fSigPanel;
            final int w = p.getSize().width, hgt = p.getSize().height;
            onEdt(new Runnable() { public void run() {
                p.mouseDown(null, w / 2, hgt / 2);
                for (int i = 1; i <= 10; i++)
                    p.mouseDrag(null, w / 2 + i * (w / 2 - 2) / 10, hgt / 2 - i * (hgt / 4) / 10);
            } });
            settle(200);
        }
        capture(name + "_a_signals");
        onEdt(new Runnable() { public void run() { conv.mouseDown(null, 0, 0); } });
        int prev = 0;
        char tag = 'b';
        for (final int stop : stops) {
            final int from = prev;
            onEdt(new Runnable() { public void run() {
                for (int x = from + 1; x <= stop; x++) conv.mouseDrag(null, x, 0);
            } });
            settle(250);
            capture(name + "_" + (tag++) + "_t" + stop);
            prev = stop;
        }
        writeJson(name);
    }

    static void press(ControllableSignal c, String which) throws Exception {
        SigControls sc = (SigControls) c.getComponent(1);
        final SigButton b = which.equals("pulse") ? sc.fPulseButton
                : which.equals("double pulse") ? sc.fDoublePulseButton
                : which.equals("decay") ? sc.fDecayButton : sc.fClearButton;
        onEdt(new Runnable() { public void run() { b.mouseDown(null, 1, 1); } });
        settle(200);
    }

    static void capture(final String name) throws Exception {
        final BufferedImage img = new BufferedImage(480, 600, BufferedImage.TYPE_INT_RGB);
        onEdt(new Runnable() { public void run() {
            Graphics g = img.getGraphics();
            g.setColor(applet.getBackground() == null ? Color.lightGray : applet.getBackground());
            g.fillRect(0, 0, 480, 600);
            applet.printAll(g);
            g.dispose();
        } });
        ImageIO.write(img, "png", new File(outDir, name + ".png"));
    }

    static void writeJson(String name) throws Exception {
        PrintWriter w = new PrintWriter(new File(outDir, name + ".json"), "UTF-8");
        w.println("{");
        w.println("  \"source\": \"original applet (Crutchfield, JHU 1996) run by tools/CtProbe.java\",");
        w.println("  \"fT\": " + conv.fT + ", \"fOffset\": " + conv.fOffset + ", \"fPrevX\": " + conv.fPrevX + ",");
        w.println("  \"x\": " + arr(sig(cx).values()) + ",");
        w.println("  \"h\": " + arr(sig(ch).values()) + ",");
        w.println("  \"integrand\": " + arr(integ.getSignal().values()) + ",");
        w.println("  \"y\": " + arr(ypanel.getSignal().values()) + ",");
        boolean[] shown = ((ConvSignal) ypanel.getSignal()).shown;
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < shown.length; i++) sb.append(i > 0 ? "," : "").append(shown[i] ? 1 : 0);
        w.println("  \"y_shown\": " + sb + "]");
        w.println("}");
        w.close();
    }

    static String arr(int[] a) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < a.length; i++) sb.append(i > 0 ? "," : "").append(a[i]);
        return sb.append("]").toString();
    }

    static void dumpTree(PrintWriter w, Component c, int ox, int oy, int depth) {
        Rectangle r = c.getBounds();
        int ax = depth == 0 ? 0 : ox + r.x, ay = depth == 0 ? 0 : oy + r.y;
        StringBuilder ind = new StringBuilder();
        for (int i = 0; i < depth; i++) ind.append("  ");
        String extra = "";
        if (c instanceof SigPanel) extra = " name=\"" + ((SigPanel) c).fName + "\"";
        if (c instanceof Label) extra = " text=\"" + ((Label) c).getText() + "\"";
        w.println(ind + c.getClass().getSimpleName() + extra + " abs=(" + ax + "," + ay + ","
                + r.width + "," + r.height + ")");
        if (c instanceof Container)
            for (Component k : ((Container) c).getComponents()) dumpTree(w, k, ax, ay, depth + 1);
    }

    static void onEdt(Runnable r) throws Exception { EventQueue.invokeAndWait(r); }

    static void settle(int ms) throws Exception {
        Thread.sleep(ms);
        onEdt(new Runnable() { public void run() {} });
    }
}
