from manim import (
    Scene, Text, Write, Create, UP, DOWN, RIGHT,
    WHITE, ORANGE, BLUE_C, GREEN_C, YELLOW_C,
    VGroup, Rectangle, FadeOut, Group, config
)


class MultiLayerAESWorkflow(Scene):
    def construct(self):
        # Set resolution to full HD (1080p)
        config.pixel_height = 1080
        config.pixel_width = 1920
        config.frame_height = 9  # Adjusted from 8
        config.frame_width = 16  # Adjusted from 14.22
        config.frame_rate = 30
        config.background_opacity = 1
        
        # Adjust scale factors for better fitting
        SCALE_FACTOR = 0.85  # Reduced from 1.0
        TEXT_SCALE = 0.7     # Reduced from 0.8
        PROCESS_COLOR = BLUE_C
        LAYER_COLORS = [BLUE_C, GREEN_C, YELLOW_C]
        
        # Title with description
        title = Text("Multi-Layer AES Steganography", font_size=36)
        subtitle = Text(
            "Secure Data Hiding with Multiple Encryption Layers",
            font_size=24,
            color=BLUE_C
        ).scale(SCALE_FACTOR)
        
        # Increased top buffer to prevent cutting
        title.to_edge(UP, buff=0.8)  # Changed from 0.4 to 0.8
        subtitle.next_to(title, DOWN, buff=0.3)  # Slightly increased from 0.2 to 0.3
        
        # Title sequence with longer duration
        self.play(Write(title), run_time=1.5)
        self.wait(0.5)  # Pause to let viewers read
        self.play(Write(subtitle), run_time=1.5)
        self.wait(1)  # Longer pause after introduction
        
        # === ENCODING PHASE ===
        encoding_title = Text("Encoding Process", font_size=28, color=ORANGE)
        encoding_title.next_to(subtitle, DOWN, buff=0.3)
        
        encoding_desc = Text(
            "AES-CBC Encryption with PBKDF2",
            font_size=20,
            color=GREEN_C
        ).scale(SCALE_FACTOR)
        encoding_desc.next_to(encoding_title, DOWN, buff=0.2)
        
        self.play(Write(encoding_title), run_time=1)
        self.play(Write(encoding_desc), run_time=1)
        self.wait(0.5)  # Added pause

        # Layers with enhanced details - adjusted dimensions
        layers = VGroup(*[
            Rectangle(height=2.4, width=3.0, color=color, fill_opacity=0.15)  # Reduced sizes
            for color in LAYER_COLORS
        ]).arrange(RIGHT, buff=0.6).scale(SCALE_FACTOR)  # Reduced buffer between rectangles
        layers.next_to(encoding_desc, DOWN, buff=0.4)  # Reduced buffer

        layer_labels = VGroup(*[
            Text(f"Layer {i+1}", font_size=20, color=color)
            for i, color in enumerate(LAYER_COLORS)
        ])
        
        for label, layer in zip(layer_labels, layers):
            label.next_to(layer, UP, buff=0.15)
            label.scale(SCALE_FACTOR)

        # Layers animation with slower timing
        self.play(
            *[Create(layer, run_time=1.2) for layer in layers],
            *[Write(label, run_time=1) for label in layer_labels]
        )
        self.wait(0.5)  # Added pause

        # Detailed process steps with slower timing
        for layer in layers:
            process_steps = VGroup(
                Text("1. Salt & IV Gen", font_size=14, color=PROCESS_COLOR),
                Text("2. PBKDF2-100K", font_size=14, color=BLUE_C),
                Text("3. PKCS7 Padding", font_size=14, color=PROCESS_COLOR),
                Text("4. AES-256-CBC", font_size=14, color=BLUE_C)
            ).arrange(DOWN, buff=0.15).scale(TEXT_SCALE)
            process_steps.move_to(layer)
            self.play(Write(process_steps, run_time=1.5))
            self.wait(0.3)  # Added pause between layers

        # LSB Container with adjusted dimensions
        lsb_container = Rectangle(
            height=1.0, width=6.0,  # Reduced sizes
            color=GREEN_C,
            fill_opacity=0.15
        )
        lsb_container.next_to(layers, DOWN, buff=0.8)  # Reduced buffer
        
        lsb_text = Text("LSB Embedding", font_size=20, color=GREEN_C)
        lsb_desc = Text(
            "Bit-level Data\nIntegration",
            font_size=16,
            color=GREEN_C
        )
        
        lsb_group = VGroup(lsb_text, lsb_desc)
        lsb_group.arrange(DOWN, buff=0.1).scale(TEXT_SCALE)
        lsb_group.move_to(lsb_container)
        
        # LSB Container with slower animation
        self.play(Create(lsb_container), run_time=1)
        self.play(Write(lsb_group), run_time=1)
        self.wait(0.5)  # Added pause

        # Enhanced output description
        stego_output = Text("Stego Image", font_size=20, color=WHITE)
        stego_desc = Text("Visually Identical", font_size=16, color=WHITE)
        
        stego_group = VGroup(stego_output, stego_desc)
        stego_group.arrange(DOWN, buff=0.1).scale(TEXT_SCALE)
        stego_group.next_to(lsb_container, DOWN, buff=0.3)
        
        # Enhanced output description with slower timing
        self.play(Write(stego_group), run_time=1)
        self.wait(1.5)  # Longer pause before transition

        self.wait(1)

        # === DECODING PHASE ===
        self.play(
            FadeOut(Group(*[
                mob for mob in self.mobjects 
                if mob not in [title]
            ]), run_time=1.5)  # Slower transition
        )
        self.wait(0.5)  # Added pause

        # Enhanced decoding description
        decoding_title = Text("Decoding Process", font_size=28, color=ORANGE)
        decoding_desc = Text(
            "Multi-Layer Extraction & Decryption",
            font_size=20,
            color=GREEN_C
        ).scale(SCALE_FACTOR)
        
        decoding_title.next_to(title, DOWN, buff=0.3)
        decoding_desc.next_to(decoding_title, DOWN, buff=0.2)
        
        self.play(Write(decoding_title), Write(decoding_desc))

        # Enhanced stego input description
        stego_input = Text("Stego Image", font_size=20, color=WHITE)
        stego_input_desc = Text("Data Carrier", font_size=16, color=WHITE)
        
        stego_input_group = VGroup(stego_input, stego_input_desc)
        stego_input_group.arrange(DOWN, buff=0.1).scale(TEXT_SCALE)
        stego_input_group.next_to(decoding_desc, DOWN, buff=0.5)
        
        self.play(Write(stego_input_group))

        # Enhanced LSB extraction
        extract = Rectangle(
            height=1.2, width=7,
            color=GREEN_C,
            fill_opacity=0.15
        )
        extract.next_to(stego_input_group, DOWN, buff=0.5)
        
        extract_text = Text("LSB Extraction", font_size=20, color=GREEN_C)
        extract_desc = Text("Bit Stream Recovery", font_size=16, color=GREEN_C)
        
        extract_group = VGroup(extract_text, extract_desc)
        extract_group.arrange(DOWN, buff=0.1).scale(TEXT_SCALE)
        extract_group.move_to(extract)
        
        self.play(Create(extract), Write(extract_group))

        # Decryption layers with adjusted dimensions
        decrypt_layers = VGroup(*[
            Rectangle(height=2.4, width=3.0, color=color, fill_opacity=0.15)  # Reduced sizes
            for color in reversed(LAYER_COLORS)
        ]).arrange(RIGHT, buff=0.6).scale(SCALE_FACTOR)  # Reduced buffer
        decrypt_layers.next_to(extract, DOWN, buff=0.5)  # Reduced buffer

        # Detailed decryption process with message extraction
        for i, layer in enumerate(decrypt_layers):
            layer_text = Text(
                f"Layer {3-i}",
                font_size=18,
                color=LAYER_COLORS[2-i]
            ).scale(SCALE_FACTOR)
            layer_text.next_to(layer, UP, buff=0.1)

            process = VGroup(
                Text("1. Extract Salt/IV", font_size=14),
                Text("2. PBKDF2 Key", font_size=14),
                Text("3. AES Decrypt", font_size=14),
                Text("4. Remove Padding", font_size=14)
            ).arrange(DOWN, buff=0.12).scale(TEXT_SCALE)
            process.move_to(layer)

            # Add message extraction text with adjusted position
            message_text = Text(
                f"Message {3-i} Extracted",
                font_size=16,
                color=GREEN_C
            ).scale(TEXT_SCALE)
            message_text.next_to(layer, DOWN, buff=0.15)

            # Decryption process with slower timing
            self.play(
                Create(layer, run_time=1),
                Write(layer_text, run_time=0.8),
                Write(process, run_time=1.2)
            )
            self.wait(0.3)  # Added pause
            self.play(Write(message_text, run_time=0.8))
            self.wait(0.5)  # Added pause between layers

        self.wait(1)  # Added pause before final status
        
        # Final message status with slower timing
        final_status = Text(
            "All Messages Successfully Recovered",
            font_size=24,
            color=GREEN_C
        ).scale(SCALE_FACTOR)
        final_status.next_to(decrypt_layers, DOWN, buff=0.4)
        
        self.play(Write(final_status), run_time=1.5)
        self.wait(2)  # Longer final pause
        
        # Slower final fadeout
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.5)
        self.wait(0.5)  # Final pause


# To run with 720p:
# manim -pqh manim_script_second.py MultiLayerAESWorkflow
